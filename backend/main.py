import json
import threading
from dataclasses import dataclass
from typing import List, Optional, Literal, Callable, Tuple
import random
import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os

from pydantic import BaseModel

import gallicaGetter
import pyllicaWrapper as pyllicaWrapper
from database import connContext
from database.connContext import build_db_conn, build_redis_conn
from database.displayDataResolvers import (
    select_display_records,
    get_gallica_records_for_display,
    clear_records_for_requestid,
    get_ocr_text_for_record,
    select_csv_data_for_tickets,
    select_top_papers_for_tickets,
)
from database.graphDataResolver import select_series_for_tickets
from database.paperSearchResolver import (
    select_papers_similar_to_keyword,
    get_num_papers_in_range,
)
from database.recordInsertResolvers import (
    insert_records_into_results,
    insert_records_into_groupcounts,
)
from gallicaGetter import VolumeOccurrenceWrapper, PeriodOccurrenceWrapper
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
from gallicaGetter.fetch.progressUpdate import ProgressUpdate
from gallicaGetter.parse.parseXML import get_one_paper_from_record_batch
from gallicaGetter.parse.periodRecords import PeriodRecord
from gallicaGetter.parse.volumeRecords import VolumeRecord

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


requestID = random.randint(0, 1000000000)


@app.get("/")
def index():
    return {"message": "ok"}


class Ticket(BaseModel):
    id: int
    terms: List[str] | str
    start_date: int
    end_date: int
    codes: Optional[List[str] | str] = None
    grouping: str = "year"
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None


@app.post("/api/init")
def init(ticket: Ticket | List[Ticket]):
    global requestID
    requestID += 1
    ticket.id = requestID
    with build_redis_conn() as redis_conn:
        redis_conn.delete(f"request:{requestID}:progress")
        redis_conn.delete(f"request:{requestID}:cancelled")
    request = Request(ticket=ticket)
    request.start()
    return {"requestid": requestID}


@app.get("/poll/progress/{request_id}")
def poll_request_state(request_id: str):
    with build_redis_conn() as redis_conn:
        progress = redis_conn.get(f"request:{request_id}:progress")
        if progress:
            progress = json.loads(progress)
            request_state = progress["request_state"]
            ticket_state = progress["ticket_state"]
        else:
            request_state = "PENDING"
            ticket_state = {}
    if progress is None:
        return {"state": "PENDING"}
    return {"state": request_state, "progress": ticket_state}


@app.get("/api/revokeTask/{request_id}")
def revoke_task(request_id: int):
    with build_redis_conn() as redis_conn:
        redis_conn.set(f"request:{request_id}:cancelled", "true")
    with build_db_conn() as conn:
        clear_records_for_requestid(request_id, conn)
    return {"state": "REVOKED"}


class Paper(BaseModel):
    title: str
    code: str
    start_date: str
    end_date: str


@app.get("/api/papers/{keyword}")
def papers(keyword: str):
    with build_db_conn() as conn:
        similar_papers = select_papers_similar_to_keyword(keyword, conn)
    return similar_papers


@app.get("/api/numPapersOverRange/{start}/{end}")
def get_num_papers_over_range(start: int, end: int):
    with build_db_conn() as conn:
        count = get_num_papers_in_range(start=start, end=end, conn=conn)
    return str(count)


@app.get("/api/graphData")
def graph_data(
    request_id: int,
    grouping: Literal["day", "month", "year", "gallicaMonth", "gallicaYear"] = "year",
    average_window: Optional[int] = 0,
):
    with build_db_conn() as conn:
        items = select_series_for_tickets(
            request_id=request_id,
            grouping=grouping,
            average_window=average_window,
            conn=conn,
        )
    return {"series": items}


@app.get("/api/topPapers")
def get_top_papers(
    request_id: int, ticket_ids: List[int] = Query(), num_results: int = 10
):
    with build_db_conn() as conn:
        top_papers = select_top_papers_for_tickets(
            tickets=ticket_ids,
            request_id=request_id,
            num_results=num_results,
            conn=conn,
        )
    return {"topPapers": top_papers}


@app.get("/api/getcsv")
def get_csv(tickets: int | List[int], request_id: int):
    with build_db_conn() as conn:
        csv_data = select_csv_data_for_tickets(
            ticket_ids=tickets, request_id=request_id, conn=conn
        )
    return {"csvData": csv_data}


@app.get("/api/getDisplayRecords")
def records(
    request_id: int,
    ticket_ids: List[int] = Query(),
    term: str = None,
    periodical: str = None,
    year: int = None,
    month: int = None,
    day: int = None,
    limit: int = 10,
    offset: int = 0,
):
    with build_db_conn() as conn:
        db_records, count = select_display_records(
            ticket_ids=ticket_ids,
            request_id=request_id,
            term=term,
            periodical=periodical,
            limit=limit,
            offset=offset,
            year=year,
            month=month,
            day=day,
            conn=conn,
        )
    return {"displayRecords": db_records, "count": count}


@app.get("/api/getGallicaRecords")
def fetch_records_from_gallica(
    year: int = None,
    month: int = None,
    day: int = None,
    terms: List[str] = Query(),
    codes: Optional[List[str]] = Query(None),
    start_index: int = 0,
    num_results: int = 10,
    link_term: str = None,
    link_distance: int = None,
):
    gallica_records = get_gallica_records_for_display(
        terms=terms,
        codes=codes,
        year=year,
        month=month,
        day=day,
        offset=start_index,
        limit=num_results,
        link_term=link_term,
        link_distance=link_distance,
    )
    if gallica_records:
        if isinstance(gallica_records[0], VolumeRecord):
            display_records = [
                (
                    volume_occurrence.term,
                    volume_occurrence.paper_title,
                    volume_occurrence.date.getYear(),
                    volume_occurrence.date.getMonth(),
                    volume_occurrence.date.getDay(),
                    volume_occurrence.url,
                )
                for volume_occurrence in gallica_records
            ]
        elif isinstance(gallica_records[0], PeriodRecord):
            display_records = [
                (
                    period_record.term,
                    period_record.date.getYear(),
                    period_record.date.getMonth(),
                    period_record.date.getDay(),
                    period_record.count,
                )
                for period_record in gallica_records
            ]
        else:
            raise ValueError(f"Unknown record type: {type(gallica_records[0])}")
    else:
        display_records = []
    return {"displayRecords": display_records}


@app.get("/api/ocrtext/{ark_code}/{term}")
def ocr_text(ark_code: str, term: str):
    record = get_ocr_text_for_record(ark_code=ark_code, term=term)
    return {"numResults": record.num_results, "text": record.pages}


class Request(threading.Thread):
    def __init__(self, ticket: Ticket, conn=None):
        self.numResultsDiscovered = 0
        self.ticket = ticket
        self.progress_stats = Progress(ticketID=ticket.id, grouping=ticket.grouping)
        self.conn = conn
        self.num_records = 0
        super().__init__()

    def post_progress_to_redis(self, redis_conn):
        redis_conn.set(
            f"request:{self.requestID}:progress",
            json.dumps(self.progress_stats.to_dict()),
        )

    def set_total_records_for_ticket_progress(self, ticket_id: int, total_records: int):
        self.progress_stats[ticket_id].total_items = total_records

    def run(self):
        with connContext.build_redis_conn() as redis_conn:
            with self.conn or connContext.build_db_conn() as db_conn:
                db_space_remaining = (
                    MAX_DB_SIZE - get_number_rows_in_db(conn=db_conn) - 10000
                )

                self.num_records, self.tickets = get_num_records_for_args(
                    self.tickets,
                    onNumRecordsFound=self.set_total_records_for_ticket_progress,
                )

                # update groupings that might have changed so the frontend knows
                for ticket in self.tickets:
                    self.progress_stats[ticket.id].grouping = ticket.grouping

                if self.num_records == 0:
                    self.state = "NO_RECORDS"
                elif self.num_records > min(db_space_remaining, RECORD_LIMIT):
                    self.state = "TOO_MANY_RECORDS"
                else:
                    for ticket in self.tickets:
                        get_and_insert_records_for_args(
                            ticketID=ticket.id,
                            requestID=self.requestID,
                            args=ticket,
                            onProgressUpdate=lambda stats: self.update_progress_and_post_redis(
                                redis_conn=redis_conn,
                                ticket_id=ticket.id,
                                progress=stats,
                            ),
                            onAddingMissingPapers=lambda: self.progress_stats[
                                ticket.id
                            ].set_search_state("ADDING_MISSING_PAPERS"),
                            conn=db_conn,
                        )
                        self.progress_stats[ticket.id].search_state = "COMPLETED"
                        self.post_progress_to_redis(redis_conn)
                    self.state = "COMPLETED"
        self.post_progress_to_redis(redis_conn)

    def update_progress_and_post_redis(
        self, ticket_id: int, progress: ProgressUpdate, redis_conn
    ):
        self.progress_stats[ticket_id].update_progress(progress)
        self.post_progress_to_redis(redis_conn)
        if redis_conn.get(f"request:{self.requestID}:cancelled") == b"true":
            raise KeyboardInterrupt


def get_number_rows_in_db(conn):
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT sum(reltuples)::bigint AS estimate
            FROM pg_class
            WHERE relname IN ('results', 'papers');
            """
        )
        return curs.fetchone()[0]


def get_num_records_for_args(
    tickets: List[Ticket],
    onNumRecordsFound: Optional[Callable[[int, int], None]] = None,
) -> Tuple[int, List[Ticket]]:

    total_records = 0
    cachable_responses = {}

    for index, ticket in enumerate(tickets):

        # get total record so we can tell the user if there are no records, regardless of search type
        base_queries_with_num_results = get_num_records_all_volume_occurrence(ticket)
        num_records = sum(query.num_results for query in base_queries_with_num_results)

        if ticket.grouping == "all" or ticket.codes:

            # Don't make more requests than there are records, only applies to code-filtered requests,
            # which cannot use Pyllica, which is only one request (I think, it's been a while)

            if ticket.codes and ticket.grouping in ["year", "month"]:
                num_periods_to_fetch = get_num_periods_in_range_for_grouping(
                    grouping=ticket.grouping,
                    start=ticket.start_date,
                    end=ticket.end_date,
                )
                if num_periods_to_fetch > (num_records // 50) + 1:

                    # update ticket so we don't make more requests than there are record batches

                    tickets[index] = Ticket(
                        id=ticket.id,
                        terms=ticket.terms,
                        start_date=ticket.start_date,
                        end_date=ticket.end_date,
                        codes=ticket.codes,
                        grouping="all",
                        link_term=ticket.link_term,
                        link_distance=ticket.link_distance,
                    )
                else:
                    num_records = num_periods_to_fetch

            total_records += num_records
            cachable_responses.update({ticket.id: base_queries_with_num_results})
        else:
            if num_records:
                total_records += get_num_periods_in_range_for_grouping(
                    grouping=ticket.grouping,
                    start=ticket.start_date,
                    end=ticket.end_date,
                )
            else:
                total_records += num_records
        onNumRecordsFound and onNumRecordsFound(ticket.id, total_records)

    if cachable_responses:
        # create new args for args with cached responses
        new_tickets = []
        for ticket in tickets:
            if cached_queries := cachable_responses.get(ticket.id):
                new_tickets.append(
                    TicketWithCachedResponse(
                        id=ticket.id,
                        terms=ticket.terms,
                        start_date=ticket.start_date,
                        end_date=ticket.end_date,
                        codes=ticket.codes,
                        link_term=ticket.link_term,
                        link_distance=ticket.link_distance,
                        grouping=ticket.grouping,
                        cached_response=cached_queries,
                    )
                )
            else:
                new_tickets.append(ticket)
        tickets = new_tickets
    return total_records, tickets


def get_num_periods_in_range_for_grouping(grouping: str, start: int, end: int) -> int:
    start, end = int(start), int(end)
    if grouping == "year":
        return end - start + 1
    elif grouping == "month":
        return (end - start + 1) * 12
    else:
        raise ValueError(f"Invalid grouping: {grouping}")


def get_num_records_all_volume_occurrence(args: Ticket) -> List[OccurrenceQuery]:
    api = gallicaGetter.connect("volume")
    base_queries_with_num_results = api.get_num_results_for_args(
        terms=args.terms,
        start_date=args.start_date,
        end_date=args.end_date,
        codes=args.codes,
        link_term=args.link_term,
        link_distance=args.link_distance,
    )
    return base_queries_with_num_results


@dataclass(slots=True)
class Progress:
    ticketID: int
    grouping: str
    num_items_fetched: int = 0
    total_items: int = 0
    average_response_time: float = 0
    estimate_seconds_to_completion: Optional[float] = None
    randomPaper: Optional[str] = None
    search_state: str = "PENDING"

    def set_search_state(self, state: str):
        self.search_state = state

    def to_dict(self):
        return {
            "numResultsDiscovered": self.total_items,
            "numResultsRetrieved": self.num_items_fetched,
            "progressPercent": self.total_items
            and (self.num_items_fetched / self.total_items) * 100
            or 0,
            "estimateSecondsToCompletion": self.estimate_seconds_to_completion,
            "randomPaper": self.randomPaper,
            "randomText": None,
            "state": self.search_state,
            "grouping": self.grouping,
        }

    def update_progress(self, stats: ProgressUpdate):
        if self.search_state == "PENDING":
            self.search_state = "RUNNING"

        # all search items measured in records, other searches in requests fetched. a bit confusing, maybe.
        if self.grouping == "all":
            self.num_items_fetched += 50
        else:
            self.num_items_fetched += 1

        # estimate number of seconds to completion
        num_remaining_cycles = (
            self.total_items - self.num_items_fetched
        ) / stats.num_workers
        if self.grouping == "all":
            num_remaining_cycles /= 50

        if self.average_response_time:
            self.average_response_time = (
                self.average_response_time + stats.elapsed_time
            ) / 2
        else:
            self.average_response_time = stats.elapsed_time

        # a bit of reader fluff to make the wait enjoyable
        self.randomPaper = get_one_paper_from_record_batch(stats.xml)
        self.estimate_seconds_to_completion = (
            self.average_response_time * num_remaining_cycles
        )


def get_and_insert_records_for_args(
    ticketID: int,
    requestID: int,
    args: Ticket,
    onProgressUpdate: callable,
    conn,
    api=None,
    onAddingMissingPapers: callable = None,
):
    match [args.grouping, bool(args.codes)]:
        case ["all", True] | ["all", False]:
            all_volume_occurrence_search_ticket(
                ticket=args,
                requestID=requestID,
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate,
                onAddingMissingPapers=onAddingMissingPapers,
                api=api,
            )
        case ["year", False] | ["month", False]:
            pyllica_search_ticket(
                args=args, requestID=requestID, ticketID=ticketID, conn=conn
            )
        case ["year", True] | ["month", True]:
            period_occurrence_search_ticket(
                args=args,
                requestID=requestID,
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate,
                api=api,
            )
        case _:
            raise ValueError(f"Invalid search type: {args.grouping}, {args.codes}")


@dataclass(frozen=True, slots=True)
class TicketWithCachedResponse:
    id: int
    terms: List[str] | str
    start_date: int
    end_date: int
    cached_response: List[OccurrenceQuery]
    codes: Optional[List[str] | str] = None
    grouping: str = "year"
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None


def all_volume_occurrence_search_ticket(
    ticket: Ticket | TicketWithCachedResponse,
    conn,
    onProgressUpdate: callable,
    onAddingMissingPapers: callable,
    requestID: int,
    ticketID: int,
    api=None,
):
    api: VolumeOccurrenceWrapper = gallicaGetter.connect("volume", api=api)
    records = api.get(
        terms=ticket.terms,
        start_date=ticket.start_date,
        end_date=ticket.end_date,
        codes=ticket.codes,
        link_term=ticket.link_term,
        link_distance=ticket.link_distance,
        onProgressUpdate=onProgressUpdate,
        query_cache=type(ticket) == TicketWithCachedResponse and ticket.cached_response,
        generate=True,
        num_workers=50,
    )
    insert_records_into_db(
        records=records,
        insert_into_results=True,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
        onAddingMissingPapers=onAddingMissingPapers,
    )


def pyllica_search_ticket(args: Ticket, conn, requestID: int, ticketID: int):
    records = pyllicaWrapper.get(args)
    insert_records_into_db(
        records=records,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
    )


def period_occurrence_search_ticket(
    args: Ticket,
    requestID: int,
    ticketID: int,
    conn,
    onProgressUpdate: callable,
    api=None,
):
    api: PeriodOccurrenceWrapper = gallicaGetter.connect("period", api=api)
    records = api.get(
        terms=args.terms,
        codes=args.codes,
        start_date=args.start_date,
        end_date=args.end_date,
        onProgressUpdate=onProgressUpdate,
        num_workers=50,
        grouping=args.grouping,
    )
    insert_records_into_db(
        records=records,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
    )


def insert_records_into_db(
    records: List,
    conn,
    requestID: int,
    ticketID: int,
    insert_into_results: bool = False,
    onAddingMissingPapers: callable = None,
):
    if insert_into_results:
        insert_records_into_results(
            records=records,
            conn=conn,
            requestID=requestID,
            ticketID=ticketID,
            onAddingMissingPapers=onAddingMissingPapers,
        )
    else:
        insert_records_into_groupcounts(
            records=records, conn=conn, requestID=requestID, ticketID=ticketID
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
