import threading
from dataclasses import dataclass
from typing import Optional
import gallicaGetter
from gallicaGetter.parse.parseXML import get_one_paper_from_record_batch
from gallicaGetter.searchArgs import SearchArgs
from typing import List
from appsearch.search import get_and_insert_records_for_args

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000


class Request(threading.Thread):
    def __init__(self, identifier, arg_bundles, conn):
        self.numResultsDiscovered = 0
        self.state = 'RUNNING'
        self.requestID = identifier
        self.args_for_searches = {
            ticketID: SearchArgs(**args)
            for ticketID, args in arg_bundles.items()
        }
        self.progress_stats = {
            key: SearchProgressStats(ticketID=key)
            for key, _ in self.args_for_searches.items()
        }
        self.conn = conn
        super().__init__()

    def get_progress_stats(self):
        return {
            key: self.progress_stats[key].to_dict()
            for key in self.args_for_searches.keys()
        }

    def run(self):
        db_space_remaining = MAX_DB_SIZE - self.get_number_rows_in_db() - 10000
        num_records = get_num_records_for_args(list(self.args_for_searches.values()))
        if num_records == 0:
            self.state = 'NO_RECORDS'
        elif num_records > min(db_space_remaining, RECORD_LIMIT):
            self.state = 'TOO_MANY_RECORDS'
        else:
            for ticketID, args in self.args_for_searches.items():
                get_and_insert_records_for_args(
                    ticketID=ticketID,
                    args=args,
                    onProgressUpdate=lambda progressStats:
                        self.progress_stats[ticketID].update_progress(**progressStats),
                    conn=self.conn
                )
                self.progress_stats[ticketID].state = 'COMPLETED'
            self.state = 'COMPLETED'

    def get_number_rows_in_db(self):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                SELECT sum(reltuples)::bigint AS estimate
                FROM pg_class
                WHERE relname IN ('results', 'papers');
                """
            )
            return curs.fetchone()[0]


def get_num_records_for_args(args_for_tickets: List[SearchArgs]) -> int:
    total_records = 0
    for args in args_for_tickets:
        if args.grouping == 'all':
            total_records += get_num_records_all_volume_occurrence(args)
        else:
            total_records += get_num_periods_in_range_for_grouping(
                grouping=args.grouping,
                start=args.start_date,
                end=args.end_date
            )
    return total_records


def get_num_periods_in_range_for_grouping(grouping: str, start: str, end: str) -> int:
    start, end = int(start), int(end)
    if grouping == 'year':
        return end - start + 1
    elif grouping == 'month':
        return (end - start + 1) * 12
    else:
        raise ValueError(f'Invalid grouping: {grouping}')


def get_num_records_all_volume_occurrence(args: SearchArgs) -> int:
    api = gallicaGetter.connect('volume')
    base_queries_with_num_results = api.get_num_results_for_args(
        terms=args.terms,
        start_date=args.start_date,
        end_date=args.end_date,
        codes=args.codes,
        link_term=args.link_term,
        link_distance=args.link_distance,
    )
    return sum(query.num_results for query in base_queries_with_num_results)


@dataclass(slots=True)
class SearchProgressStats:
    ticketID: str
    num_retrieved_batches: int = 0
    total_records = 0
    average_response_time: float = 0
    estimate_seconds_to_completion: Optional[float] = None
    randomPaper: Optional[str] = None
    search_state: str = 'PENDING'

    def to_dict(self):
        return {
            'numResultsDiscovered': self.total_records,
            'numResultsRetrieved': self.num_retrieved_batches * 50,
            'progressPercent': self.num_retrieved_batches / self.num_batches,
            'estimateSecondsToCompletion': self.estimate_seconds_to_completion,
            'randomPaper': self.randomPaper,
            'randomText': None,
            'active': self.search_state == 'RUNNING'
        }

    def update_progress(
            self,
            elapsedTime,
            numWorkers,
            xml
    ):
        if self.search_state == 'PENDING':
            self.search_state = 'RUNNING'
        self.num_retrieved_batches += 1
        if self.average_response_time:
            self.average_response_time = (self.average_response_time + elapsedTime) / 2
        else:
            self.average_response_time = elapsedTime
        self.randomPaper = get_one_paper_from_record_batch(xml)
        num_remaining_cycles = (self.num_batches - self.num_retrieved_batches) / numWorkers
        self.estimate_seconds_to_completion = self.average_response_time * num_remaining_cycles
