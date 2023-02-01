import json
import os
import random
from gallicaGetter.www.progress import Progress
from gallicaGetter.www.contextPair import ContextPair
import io
import threading
from typing import Any, Callable, Generator, List, Literal, Optional, Tuple
from gallicaGetter.wrapperFactory import WrapperFactory
from gallicaGetter.fetch.progressUpdate import ProgressUpdate
from gallicaGetter.parse.paperRecords import PaperRecord
from gallicaGetter.parse.parseXML import get_one_paper_from_record_batch
from gallicaGetter.parse.periodRecords import PeriodRecord
from gallicaGetter.parse.volumeRecords import VolumeRecord
from gallicaGetter.www.progress import Progress
from gallicaGetter.www.ticket import Ticket
import gallicaGetter.www.pyllicaWrapper as pyllicaWrapper
import uvicorn
from database.connContext import build_db_conn, build_redis_conn
from database.displayDataResolvers import (
    clear_records_for_requestid,
    select_display_records,
    make_date_from_year_mon_day,
)
from database.graphDataResolver import build_highcharts_series
from database.paperSearchResolver import (
    get_num_papers_in_range,
    select_papers_similar_to_keyword,
)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from gallicaGetter.parse.contentRecord import GallicaContext
from pydantic import BaseModel

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
                num_requests_to_send=0,
                num_requests_sent=0,
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
    """Paper search dropdown route"""
    with build_db_conn() as conn:
        similar_papers = select_papers_similar_to_keyword(keyword, conn)
    return similar_papers


@app.get("/api/numPapersOverRange/{start}/{end}")
def get_num_papers_over_range(start: int, end: int):
    """Number of papers that published in a year between start and end."""
    with build_db_conn() as conn:
        count = get_num_papers_in_range(start=start, end=end, conn=conn)
    return str(count)


@app.get("/api/graphData")
def graph_data(
    request_id: int,
    grouping: Literal["month", "year"] = "year",
    backend_source: Literal["gallica", "pyllica"] = "pyllica",
    average_window: int = 0,
):
    with build_db_conn() as conn:
        return build_highcharts_series(
            request_id=request_id,
            grouping=grouping,
            backend_source=backend_source,
            average_window=average_window,
            conn=conn,
        )


@app.get("/api/getDisplayRecords")
def records(
    request_id: int,
    ticket_ids: List[int] = Query(),
    term: str = "",
    periodical: str = "",
    year: int = 0,
    month: int = 0,
    day: int = 0,
    limit: int = 10,
    offset: int = 0,
):
    """Gets records stored in the database, as opposed to fetching them from Gallica."""
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
    context: GallicaContext


class GallicaResponse(BaseModel):
    records: List[GallicaRecord]
    num_results: int


@app.get("/api/gallicaRecords")
def fetch_records_from_gallica(
    year: Optional[int] = 0,
    month: Optional[int] = 0,
    day: Optional[int] = 0,
    terms: List[str] = Query(),
    codes: Optional[List[str]] = Query(None),
    cursor: Optional[int] = 0,
    limit: Optional[int] = 10,
    link_term: Optional[str] = None,
    link_distance: Optional[int] = 0,
    source: Literal["book", "periodical", "all"] = "all",
    sort: Literal["date", "relevance"] = "relevance",
) -> GallicaResponse:
    """API endpoint for the context table."""
    link = None
    if link_term and not link_distance or link_distance and not link_term:
        raise HTTPException(
            status_code=400,
            detail="link_distance and link_term must both be specified if either is specified",
        )
    if link_distance and link_term:
        link_distance = int(link_distance)
        link = (link_term, link_distance)

    total_records = 0

    def set_total_records(num_records: int):
        """Callback passed to the volume wrapper"""
        nonlocal total_records
        total_records = num_records

    # fetch the volumes in which terms appear
    volume_Gallica_wrapper = WrapperFactory.connect_volume()
    gallica_records = volume_Gallica_wrapper.get(
        terms=terms,
        start_date=make_date_from_year_mon_day(year, month, day),
        codes=codes,
        source=source,
        link=link,
        num_results=limit,
        start_index=cursor,
        sort=sort,
        on_get_total_records=set_total_records,
    )

    # fetch the context for those terms
    content_wrapper = WrapperFactory.connect_context()
    keyed_records = {record.url.split("/")[-1]: record for record in gallica_records}
    context = content_wrapper.get(
        [
            ContextPair(ark_code=record.url.split("/")[-1], term=record.term)
            for _, record in keyed_records.items()
        ]
    )

    # combine the two
    records_with_context: List[GallicaRecord] = []
    for record in context:
        corresponding_record = keyed_records[record.ark]
        records_with_context.append(
            GallicaRecord(
                paper_title=corresponding_record.paper_title,
                paper_code=corresponding_record.paper_code,
                term=corresponding_record.term,
                date=str(corresponding_record.date),
                url=corresponding_record.url,
                context=record,
            )
        )

    return GallicaResponse(records=records_with_context, num_results=total_records)


class Request(threading.Thread):
    """A thread that spawns for each user and calls the core fetch --> parse --> store to database logic"""

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

    def post_progress_to_redis(self, redis_conn):
        """Redis progress is polled by the frontend to show progress to the user."""
        progress = Progress(
            num_results_discovered=self.num_records,
            num_requests_to_send=self.total_requests,
            num_requests_sent=self.num_requests_sent,
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
        """Fetch records for user from Gallica or Pyllica and insert to DB for graphing"""
        with build_redis_conn() as redis_conn:
            with self.conn or build_db_conn() as db_conn:
                if self.ticket.codes:
                    self.ticket.backend_source = "gallica"
                    self.num_records, self.ticket = get_num_records_on_gallica_for_args(
                        ticket=self.ticket,
                        on_num_records_found=self.set_total_records_for_ticket_progress,
                    )
                else:
                    # Too slow to check for a null request by asking Gallica,
                    # so just assume there are records for now, pass a callback
                    # to Pyllica wrapper that will update frontend if null request
                    self.ticket.backend_source = "pyllica"
                    self.num_records = 1

                # Inform frontend of total number of records
                self.post_progress_to_redis(redis_conn=redis_conn)

                if self.num_records == 0:
                    self.state = "no_records"
                elif self.num_records > 100000000:
                    self.state = "too_many_records"
                else:
                    get_and_insert_records_for_ticket(
                        ticket=self.ticket,
                        on_progress_update=lambda stats: self.update_progress_and_post_redis(
                            redis_conn=redis_conn,
                            progress=stats,
                        ),
                        on_pyllica_no_records_found=self.set_no_records,
                        conn=db_conn,
                    )
                    if self.state not in ["too_many_records", "no_records"]:
                        self.state = "completed"
                    self.post_progress_to_redis(redis_conn)

    def set_no_records(self):
        self.state = "no_records"

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
        """Callback passed to the fetcher to update the progress of the request"""
        self.num_requests_sent += 1

        # estimate number of seconds to completion
        num_remaining_cycles = (
            self.total_requests - self.num_requests_sent
        ) / progress.num_workers

        if self.average_response_time:
            self.average_response_time = (
                self.average_response_time + progress.elapsed_time
            ) / 2
        else:
            self.average_response_time = progress.elapsed_time

        # a bit of reader fluff to make the wait enjoyable
        self.random_paper_for_progress = get_one_paper_from_record_batch(progress.xml)
        self.estimate_seconds_to_completion = int(
            self.average_response_time * num_remaining_cycles
        )
        self.post_progress_to_redis(redis_conn)
        if redis_conn.get(f"request:{self.ticket.id}:cancelled") == b"true":
            raise KeyboardInterrupt


def get_num_records_on_gallica_for_args(
    ticket: Ticket,
    on_num_records_found: Optional[Callable[[int], None]] = None,
) -> Tuple[int, Ticket]:
    """Will possibly return a new ticket if it would be faster to query all records instead of all periods in search"""
    total_records = 0
    cached_queries = []

    api = WrapperFactory.connect_volume()
    base_queries_with_num_results = api.get_num_results_for_args(
        terms=ticket.terms,
        start_date=str(ticket.start_date),
        end_date=str(ticket.end_date),
        codes=ticket.codes,
        link=ticket.link,
        source=ticket.source,
    )
    num_records = sum(query.num_results for query in base_queries_with_num_results)

    # Ensure we don't make more requests than there are tickets. Switch to fetching all
    # records if so, faster to group ourselves on DB
    if ticket.grouping != "all":
        num_periods_to_fetch = get_num_periods_in_range_for_grouping(
            grouping=ticket.grouping,
            start=ticket.start_date,
            end=ticket.end_date,
        )
        # more requests to be sent than if we just fetched all the records ?
        if num_periods_to_fetch > (num_records // 50) + 1:
            ticket = Ticket(
                id=ticket.id,
                terms=ticket.terms,
                start_date=ticket.start_date,
                end_date=ticket.end_date,
                codes=ticket.codes,
                grouping="all",
                link=ticket.link,
                backend_source=ticket.backend_source,
            )
        else:
            num_records = num_periods_to_fetch
        total_records += num_records
        cached_queries = base_queries_with_num_results
    if num_records and ticket.grouping != "all":
        total_records += get_num_periods_in_range_for_grouping(
            grouping=ticket.grouping,
            start=ticket.start_date,
            end=ticket.end_date,
        )
    else:
        total_records += num_records

    if on_num_records_found:
        on_num_records_found(total_records)

    if cached_queries:
        ticket = Ticket(
            id=ticket.id,
            terms=ticket.terms,
            start_date=ticket.start_date,
            end_date=ticket.end_date,
            codes=ticket.codes,
            link=ticket.link,
            source=ticket.source,
            grouping=ticket.grouping,
            cached_response=cached_queries,
            backend_source=ticket.backend_source,
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


def get_and_insert_records_for_ticket(
    ticket: Ticket,
    on_progress_update: Callable,
    conn,
    on_pyllica_no_records_found: Callable,
    api=None,
):
    if ticket.backend_source == "gallica":
        if ticket.grouping == "all":
            volume_api = WrapperFactory.connect_volume(api=api)
            records = volume_api.get(
                terms=ticket.terms,
                start_date=str(ticket.start_date),
                end_date=str(ticket.end_date),
                codes=ticket.codes,
                link=ticket.link,
                source=ticket.source,
                onProgressUpdate=on_progress_update,
                query_cache=ticket.cached_response,
            )
            insert_records_into_db(
                records_for_db=records,
                insert_into_results=True,
                conn=conn,
                request_id=ticket.id or 0,
            )
        elif ticket.grouping in ["year", "month"]:
            period_api = WrapperFactory.connect_period(api=api)
            period_records = period_api.get(
                terms=ticket.terms,
                codes=ticket.codes,
                start_date=str(ticket.start_date),
                end_date=str(ticket.end_date),
                onProgressUpdate=on_progress_update,
                grouping=ticket.grouping,
            )
            insert_records_into_db(
                records_for_db=period_records,
                conn=conn,
                request_id=ticket.id or 0,
            )
        else:
            raise ValueError(f"Invalid grouping: {ticket.grouping}")
    elif ticket.backend_source == "pyllica":
        pyllica_records = pyllicaWrapper.get(
            ticket, on_no_records_found=on_pyllica_no_records_found
        )
        if pyllica_records:
            insert_records_into_db(
                records_for_db=pyllica_records, conn=conn, request_id=ticket.id or 0
            )
    else:
        raise ValueError(f"Invalid backend_source: {ticket.backend_source}")


def insert_records_into_db(
    records_for_db: Generator[Any, None, None],
    conn,
    request_id: int,
    insert_into_results: bool = False,
):
    if insert_into_results:
        insert_records_into_results(
            records=records_for_db,
            conn=conn,
            request_id=request_id,
        )
    else:
        insert_records_into_groupcounts(
            records=records_for_db, conn=conn, request_id=request_id
        )


def insert_records_into_papers(records, conn):
    csvStream = build_csv_stream(records)
    with conn.cursor() as curs:
        curs.copy_from(csvStream, "papers", sep="|")


def insert_records_into_results(records, request_id, conn):
    stream, codes = build_csv_stream_ensure_no_issue_duplicates(
        records=records,
        request_id=request_id,
    )
    if not codes:
        return
    codes_in_db = set(
        match[0] for match in get_db_codes_that_match_these_codes(codes, conn)
    )
    missing_codes = codes - codes_in_db
    if missing_codes:
        insert_missing_codes_into_db(missing_codes, conn=conn)
    with conn.cursor() as curs:
        curs.copy_from(
            stream,
            "results",
            sep="|",
            columns=(
                "identifier",
                "year",
                "month",
                "day",
                "searchterm",
                "requestid",
                "papercode",
                "papertitle",
            ),
        )


def insert_records_into_groupcounts(records, request_id, conn):
    stream = build_csv_stream(records=records, request_id=request_id)
    with conn.cursor() as curs:
        curs.copy_from(
            stream,
            "groupcounts",
            sep="|",
            columns=(
                "year",
                "month",
                "day",
                "searchterm",
                "requestid",
                "count",
            ),
        )


def insert_missing_codes_into_db(codes, conn):
    paper_api = WrapperFactory.connect_papers()
    paper_records = paper_api.get(list(codes))
    insert_records_into_papers(paper_records, conn)


def get_db_codes_that_match_these_codes(codes, conn):
    with conn.cursor() as curs:
        curs.execute("SELECT code FROM papers WHERE code IN %s", (tuple(codes),))
        return curs.fetchall()


def build_csv_stream_ensure_no_issue_duplicates(
    records: List[VolumeRecord], request_id: str
):
    csv_file_like_object = io.StringIO()
    codes = set()
    code_dates = {}
    for record in records:
        record_paper = record.paper_code
        if record_paper in codes:
            if datesForCode := code_dates.get(record_paper):
                record_date = record.date.getDate()
                if datesForCode.get(record_date):
                    continue
                else:
                    datesForCode[record_date] = True
            else:
                code_dates[record.paper_code] = {record.paper_code: True}
        else:
            codes.add(record.paper_code)
        write_to_csv_stream(
            stream=csv_file_like_object,
            record=record,
            request_id=request_id,
        )
    csv_file_like_object.seek(0)
    print(f"unique codes: {codes}")
    return csv_file_like_object, codes


def build_csv_stream(records, request_id=None):
    csv_file_like_object = io.StringIO()
    for record in records:
        write_to_csv_stream(
            stream=csv_file_like_object,
            record=record,
            request_id=request_id,
        )
    csv_file_like_object.seek(0)
    return csv_file_like_object


def write_to_csv_stream(stream, record, request_id):
    if isinstance(record, VolumeRecord):
        row = (
            record.url,
            record.date.getYear(),
            record.date.getMonth(),
            record.date.getDay(),
            record.term,
            request_id,
            record.paper_code,
            record.paper_title,
        )
    elif isinstance(record, PeriodRecord):
        row = (
            record.date.getYear(),
            record.date.getMonth(),
            record.date.getDay(),
            record.term,
            request_id,
            record.count,
        )
    elif isinstance(record, PaperRecord):
        row = (
            record.title,
            record.publishing_years[0],
            record.publishing_years[-1],
            record.continuous,
            record.code,
        )
    else:
        raise Exception(f"Unknown record type{type(record)}")
    stream.write("|".join(map(clean_csv_row, row)) + "\n")


def clean_csv_row(value):
    if value is None:
        return r"\N"
    return str(value).replace("|", "\\|")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
