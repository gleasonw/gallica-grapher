import json
import os
import random
import threading
from typing import List, Optional, Literal, Callable, Tuple

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
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
from database.graphDataResolver import build_highcharts_series
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
    terms: List[str] | str
    start_date: Optional[int]
    end_date: Optional[int]
    codes: Optional[List[str] | str] = None
    grouping: Literal["all", "month", "year", "gallicaMonth", "gallicaYear"] = "year"
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
    id: Optional[int] = None
    backend_source: Literal["gallica", "pyllica"] = "pyllica"
    cached_response: Optional[List[OccurrenceQuery]] = None


@app.post("/api/init")
def init(ticket: Ticket):
    global requestID
    requestID += 1
    ticket.id = requestID
    with build_redis_conn() as redis_conn:
        redis_conn.delete(f"request:{requestID}:progress")
        redis_conn.delete(f"request:{requestID}:cancelled")
    request = Request(ticket=ticket)
    request.start()
    return {"requestid": requestID}


class Progress(BaseModel):
    num_results_discovered: int
    num_results_retrieved: int
    estimate_seconds_to_completion: int
    random_paper: str
    random_text: str
    state: Literal[
        "too_many_records",
        "completed",
        "error",
        "no_records",
        "running",
        "adding_missing_papers",
    ]
    backend_source: Literal["gallica", "pyllica"]


@app.get("/poll/progress/{request_id}")
def poll_request_state(request_id: str):
    with build_redis_conn() as redis_conn:
        progress = redis_conn.get(f"request:{request_id}:progress")
        if progress:
            progress = json.loads(progress)
            progress = Progress(**progress)
        else:
            progress = Progress(
                num_results_discovered=0,
                num_results_retrieved=0,
                estimate_seconds_to_completion=0,
                random_paper="",
                random_text="",
                state="running",
                backend_source="gallica",
            )
    return progress


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
    grouping: Literal["month", "year"] = "year",
    backend_source: Literal["gallica", "pyllica"] = "pyllica",
    average_window: Optional[int] = 0,
):
    with build_db_conn() as conn:
        return build_highcharts_series(
            request_id=request_id,
            grouping=grouping,
            backend_source=backend_source,
            average_window=average_window,
            conn=conn,
        )


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


class GallicaRecord(BaseModel):
    paper_title: str
    paper_code: str
    term: str
    date: str
    url: str


@app.get("/api/gallicaRecords")
def fetch_records_from_gallica(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
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
    if gallica_records is None:
        return []
    return [
        # TODO: a hack to get around my strange date class in VolumeRecord... potentially expensive?
        GallicaRecord(
            paper_title=record.paper_title,
            paper_code=record.paper_code,
            term=record.term,
            date=str(record.date),
            url=record.url,
        )
        for record in gallica_records
    ]


@app.get("/api/ocrtext/{ark_code}/{term}")
def ocr_text(ark_code: str, term: str):
    record = get_ocr_text_for_record(ark_code=ark_code, term=term)
    return {"numResults": record.num_results, "text": record.pages}


class Request(threading.Thread):
    def __init__(self, ticket: Ticket, conn=None):
        self.ticket = ticket
        self.conn = conn
        self.num_records = 0
        self.num_requests_sent = 0
        self.total_requests = 0
        self.average_response_time = 0
        self.random_paper_for_progress = ""
        self.estimate_seconds_to_completion = 0
        self.state: Literal[
            "too_many_records", "completed", "error", "no_records", "running"
        ] = "running"
        super().__init__()

    def update_progress_state(self, stats: ProgressUpdate):
        self.num_requests_sent += 1

        # estimate number of seconds to completion
        num_remaining_cycles = (
            self.total_requests - self.num_requests_sent
        ) / stats.num_workers

        if self.average_response_time:
            self.average_response_time = (
                self.average_response_time + stats.elapsed_time
            ) / 2
        else:
            self.average_response_time = stats.elapsed_time

        # a bit of reader fluff to make the wait enjoyable
        self.random_paper_for_progress = get_one_paper_from_record_batch(stats.xml)
        self.estimate_seconds_to_completion = (
            self.average_response_time * num_remaining_cycles
        )

    def post_progress_to_redis(self, redis_conn):
        progress = Progress(
            num_results_discovered=self.num_records,
            num_results_retrieved=self.num_requests_sent,
            backend_source=self.ticket.backend_source,
            estimate_seconds_to_completion=self.estimate_seconds_to_completion,
            random_paper=self.random_paper_for_progress,
            state=self.state,
            random_text="",
        )
        redis_conn.set(
            f"request:{self.ticket.id}:progress",
            json.dumps(progress.dict()),
        )

    def run(self):
        with connContext.build_redis_conn() as redis_conn:
            with self.conn or connContext.build_db_conn() as db_conn:
                db_space_remaining = (
                    MAX_DB_SIZE - get_number_rows_in_db(conn=db_conn) - 10000
                )

                self.num_records, self.ticket = get_num_records_for_args(
                    ticket=self.ticket,
                    on_num_records_found=self.set_total_records_for_ticket_progress,
                )

                # Inform frontend of any state changes
                self.post_progress_to_redis(redis_conn=redis_conn)

                if self.num_records == 0:
                    self.state = "no_records"
                elif (
                    self.num_records > min(db_space_remaining, RECORD_LIMIT)
                    and self.ticket.backend_source == "gallica"
                ):
                    self.state = "too_many_records"
                else:
                    get_and_insert_records_for_ticket(
                        ticket=self.ticket,
                        on_progress_update=lambda stats: self.update_progress_and_post_redis(
                            redis_conn=redis_conn,
                            progress=stats,
                        ),
                        on_adding_missing_papers=self.set_adding_missing_papers,
                        conn=db_conn,
                    )
                    self.post_progress_to_redis(redis_conn)
                    self.state = "completed"
        self.post_progress_to_redis(redis_conn)

    def set_adding_missing_papers(self):
        self.state = "adding_missing_papers"

    def set_total_records_for_ticket_progress(self, num_records):
        self.num_records = num_records
        if self.ticket.grouping == "all":
            # Fetch all the records, 50 at a time
            self.total_requests = self.num_records // 50 + 1
        elif self.ticket.grouping in ["gallicaMonth", "gallicaYear"]:
            # Fetch Gallica's count for each time period
            self.total_requests = get_num_periods_in_range_for_grouping(
                grouping=self.ticket.grouping,
                start=self.ticket.start_date,
                end=self.ticket.end_date,
            )
        else:
            # It's a request to Pyllica, so only one fetch
            self.total_requests = 1

    def update_progress_and_post_redis(self, progress: ProgressUpdate, redis_conn):
        self.update_progress_state(stats=progress)
        self.post_progress_to_redis(redis_conn)
        if redis_conn.get(f"request:{self.ticket.id}:cancelled") == b"true":
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
    ticket: Ticket,
    on_num_records_found: Optional[Callable[[int], None]] = None,
) -> Tuple[int, Ticket]:
    total_records = 0
    cached_queries = []

    # get total record so we can tell the user if there are no records, regardless of search type
    # TODO: only do this if not pyllica. if pyllica, pass a callback during the get, trigger if no records = no waiting for API
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

                ticket = Ticket(
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
        cached_queries = base_queries_with_num_results
    else:
        if num_records and ticket.grouping in ["gallicaMonth", "gallicaYear"]:
            total_records += get_num_periods_in_range_for_grouping(
                grouping=ticket.grouping,
                start=ticket.start_date,
                end=ticket.end_date,
            )
        else:
            total_records += num_records

    on_num_records_found and on_num_records_found(total_records)

    if cached_queries:
        ticket = Ticket(
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
    return total_records, ticket


def get_num_periods_in_range_for_grouping(grouping: str, start: int, end: int) -> int:
    start, end = int(start), int(end)
    if grouping == "year":
        return end - start + 1
    elif grouping == "month":
        return (end - start + 1) * 12
    else:
        raise ValueError(f"Invalid grouping: {grouping}")


def get_num_records_all_volume_occurrence(ticket: Ticket) -> List[OccurrenceQuery]:
    api = gallicaGetter.connect("volume")
    base_queries_with_num_results = api.get_num_results_for_args(
        terms=ticket.terms,
        start_date=ticket.start_date,
        end_date=ticket.end_date,
        codes=ticket.codes,
        link_term=ticket.link_term,
        link_distance=ticket.link_distance,
    )
    return base_queries_with_num_results


def get_and_insert_records_for_ticket(
    ticket: Ticket,
    on_progress_update: callable,
    conn,
    api=None,
    on_adding_missing_papers: callable = None,
):
    match [ticket.grouping, bool(ticket.codes)]:
        case ["all", True] | ["all", False]:
            ticket.backend_source = "gallica"
            all_volume_occurrence_search_ticket(
                ticket=ticket,
                conn=conn,
                on_progress_update=on_progress_update,
                on_adding_missing_papers=on_adding_missing_papers,
                api=api,
            )
        case ["year", False] | ["month", False]:
            ticket.backend_source = "pyllica"
            pyllica_search_ticket(ticket=ticket, conn=conn)
        case ["year", True] | ["month", True]:
            ticket.backend_source = "gallica"
            period_occurrence_search_ticket(
                ticket=ticket,
                conn=conn,
                on_progress_update=on_progress_update,
                api=api,
            )
        case _:
            raise ValueError(f"Invalid search type: {ticket.grouping}, {ticket.codes}")


def all_volume_occurrence_search_ticket(
    ticket: Ticket,
    conn,
    on_progress_update: callable,
    on_adding_missing_papers: callable,
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
        onProgressUpdate=on_progress_update,
        query_cache=ticket.cached_response,
        generate=True,
        num_workers=50,
    )
    insert_records_into_db(
        records_for_db=records,
        insert_into_results=True,
        conn=conn,
        request_id=requestID,
        on_adding_missing_papers=on_adding_missing_papers,
    )


def pyllica_search_ticket(ticket: Ticket, conn):
    pyllica_records = pyllicaWrapper.get(ticket)
    insert_records_into_db(
        records_for_db=pyllica_records, conn=conn, request_id=ticket.id
    )


def period_occurrence_search_ticket(
    ticket: Ticket,
    conn,
    on_progress_update: callable,
    api=None,
):
    api: PeriodOccurrenceWrapper = gallicaGetter.connect("period", api=api)
    period_records = api.get(
        terms=ticket.terms,
        codes=ticket.codes,
        start_date=ticket.start_date,
        end_date=ticket.end_date,
        onProgressUpdate=on_progress_update,
        num_workers=50,
        grouping=ticket.grouping,
    )
    insert_records_into_db(
        records_for_db=period_records,
        conn=conn,
        request_id=ticket.id,
    )


def insert_records_into_db(
    records_for_db: List,
    conn,
    request_id: int,
    insert_into_results: bool = False,
    on_adding_missing_papers: callable = None,
):
    if insert_into_results:
        insert_records_into_results(
            records=records_for_db,
            conn=conn,
            request_id=request_id,
            on_adding_missing_papers=on_adding_missing_papers,
        )
    else:
        insert_records_into_groupcounts(
            records=records_for_db, conn=conn, request_id=request_id
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
