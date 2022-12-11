import threading
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Callable

import gallicaGetter
from appsearch.search import get_and_insert_records_for_args
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
from gallicaGetter.parse.parseXML import get_one_paper_from_record_batch
from gallicaGetter.searchArgs import SearchArgs

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000


class Request(threading.Thread):
    def __init__(self, identifier: int, arg_bundles: Dict[int, Dict], conn):
        self.numResultsDiscovered = 0
        self.state = 'RUNNING'
        self.requestID = identifier
        self.args_for_searches = {
            ticketID: SearchArgs(
                terms=args['terms'],
                start_date=args['startDate'],
                end_date=args['endDate'],
                codes=args.get('codes'),
                grouping=args.get('grouping'),
                link_term=args.get('linkTerm'),
                link_distance=args.get('linkDistance'),
            )
            for ticketID, args in arg_bundles.items()
        }
        self.progress_stats = {
            key: SearchProgressStats(ticketID=key)
            for key, _ in self.args_for_searches.items()
        }
        self.conn = conn
        self.num_records = 0
        super().__init__()

    def get_progress_stats(self):
        return {
            key: self.progress_stats[key].to_dict()
            for key in self.args_for_searches.keys()
        }

    def set_total_records_for_ticket_progress(self, ticketID: int, total_records: int):
        self.progress_stats[ticketID].total_items = total_records

    def run(self):
        db_space_remaining = MAX_DB_SIZE - self.get_number_rows_in_db() - 10000
        self.num_records, self.args_for_searches = get_num_records_for_args(
            self.args_for_searches,
            onNumRecordsFound=self.set_total_records_for_ticket_progress,
        )
        if self.num_records == 0:
            self.state = 'NO_RECORDS'
        elif self.num_records > min(db_space_remaining, RECORD_LIMIT):
            self.state = 'TOO_MANY_RECORDS'
        else:
            for ticketID, args in self.args_for_searches.items():
                get_and_insert_records_for_args(
                    ticketID=ticketID,
                    requestID=self.requestID,
                    args=args,
                    onProgressUpdate=self.progress_stats[ticketID].update_progress,
                    onAddingMissingPapers=lambda: self.progress_stats[ticketID].set_search_state(
                        'ADDING_MISSING_PAPERS'),
                    conn=self.conn
                )
                self.progress_stats[ticketID].search_state = 'COMPLETED'
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


#TODO: if num records too low, switch to volume search instead of period search
def get_num_records_for_args(
        args_for_tickets: Dict[int, SearchArgs],
        onNumRecordsFound: Optional[Callable[[int, int], None]] = None
) -> Tuple[int, Dict[int, SearchArgs]]:
    total_records = 0
    cachable_responses = {}
    for ticket_id, args in args_for_tickets.items():
        if args.grouping == 'all':
            base_queries_with_num_results = get_num_records_all_volume_occurrence(args)
            total_records += sum(query.num_results for query in base_queries_with_num_results)
            cachable_responses.update({ticket_id: base_queries_with_num_results})
        else:
            total_records += get_num_periods_in_range_for_grouping(
                grouping=args.grouping,
                start=args.start_date,
                end=args.end_date
            )
        onNumRecordsFound and onNumRecordsFound(ticket_id, total_records)
    if cachable_responses:
        # create new args for args with cached responses
        new_args_for_tickets = {}
        for ticket_id, args in args_for_tickets.items():
            if cached_queries := cachable_responses.get(ticket_id):
                new_args_for_tickets[ticket_id] = SearchArgs(
                    terms=args.terms,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    codes=args.codes,
                    grouping=args.grouping,
                    link_term=args.link_term,
                    link_distance=args.link_distance,
                    query_cache=cached_queries
                )
            else:
                new_args_for_tickets[ticket_id] = args
        args_for_tickets = new_args_for_tickets
    return total_records, args_for_tickets


def get_num_periods_in_range_for_grouping(grouping: str, start: str, end: str) -> int:
    start, end = int(start), int(end)
    if grouping == 'year':
        return end - start + 1
    elif grouping == 'month':
        return (end - start + 1) * 12
    else:
        raise ValueError(f'Invalid grouping: {grouping}')


def get_num_records_all_volume_occurrence(args: SearchArgs) -> List[OccurrenceQuery]:
    api = gallicaGetter.connect('volume')
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
class SearchProgressStats:
    ticketID: str
    num_items_fetched: int = 0
    total_items: int = 0
    average_response_time: float = 0
    estimate_seconds_to_completion: Optional[float] = None
    randomPaper: Optional[str] = None
    search_state: str = 'PENDING'

    def set_search_state(self, state: str):
        self.search_state = state

    def to_dict(self):
        return {
            'numResultsDiscovered': self.total_items,
            'numResultsRetrieved': self.num_items_fetched,
            'progressPercent': self.total_items and (self.num_items_fetched / self.total_items) * 100 or 0,
            'estimateSecondsToCompletion': self.estimate_seconds_to_completion,
            'randomPaper': self.randomPaper,
            'randomText': None,
            'state': self.search_state
        }

    def update_progress(
            self,
            elapsed_time,
            num_workers,
            xml
    ):
        if self.search_state == 'PENDING':
            self.search_state = 'RUNNING'
        self.num_items_fetched += 1
        if self.average_response_time:
            self.average_response_time = (self.average_response_time + elapsed_time) / 2
        else:
            self.average_response_time = elapsed_time
        self.randomPaper = get_one_paper_from_record_batch(xml)
        num_remaining_cycles = (self.total_items - self.num_items_fetched) / num_workers
        self.estimate_seconds_to_completion = self.average_response_time * num_remaining_cycles


if __name__ == '__main__':
    import time
    from database.connContext import build_db_conn

    with build_db_conn() as conn:
        test_request = Request(
            identifier=1,
            arg_bundles={
                0: {
                    'terms': 'brazza',
                    'startDate': '1880',
                    'endDate': '1930',
                    'grouping': 'all'
                },
            },
            conn=conn
        )
        test_request.start()
        while test_request.is_alive():
            print(test_request.get_progress_stats())
            time.sleep(1)
