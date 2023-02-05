import threading
import io
from www.models import Ticket, Progress
import json
from www.database.connContext import build_db_conn, build_redis_conn
from typing import Any, Callable, Generator, List, Literal, Optional, Tuple
import gallicaGetter.wrapperFactory as wF
from gallicaGetter.concurrentFetch import ProgressUpdate
from gallicaGetter.parse_xml import get_one_paper_from_record_batch
from gallicaGetter.volumeOccurrenceWrapper import VolumeRecord
from gallicaGetter.papersWrapper import PaperRecord
from gallicaGetter.periodOccurrenceWrapper import PeriodRecord
import www.pyllicaWrapper as pW


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

    api = wF.WrapperFactory.volume()
    base_queries_with_num_results = api.get_num_results_for_args(
        terms=ticket.terms,
        start_date=str(ticket.start_date),
        end_date=str(ticket.end_date),
        codes=ticket.codes,
        link=ticket.link,
        source=ticket.source,
    )
    num_records = sum(query.gallica_results_for_params for query in base_queries_with_num_results)

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
            volume_api = wF.WrapperFactory.volume(api=api)
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
            period_api = wF.WrapperFactory.period(api=api)
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
        pyllica_records = pW.get(
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
    paper_api = wF.WrapperFactory.papers()
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
            record.terms,
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
