from database.recordInsertResolvers import (
    insert_records_into_groupcounts,
    insert_records_into_results
)
import gallicaGetter
import appsearch.pyllicaWrapper as pyllicaWrapper
from appsearch.searchMixin import SearchMixin

#TODO: clarify the hooks
#TODO: the essential mission: get the records and insert them, track progress
def build_searches_for_tickets(args_for_tickets, stateHooks, conn):
    # Pyllica has no support for specific periodical codes, so we must route requests with codes to
    # the less-accurate gallicaGetter. Bool = True if codes provided.
    search_routes = {
        ('all', True): AllSearch,
        ('all', False): AllSearch,
        ('year', False): PyllicaSearch,
        ('month', False): PyllicaSearch,
        ('year', True): GallicaGroupedSearch,
        ('month', True): GallicaGroupedSearch,
    }
    search_objs = []
    for ticketID, params in args_for_tickets.items():
        init_params = {
            'identifier': ticketID,
            'input_args': params,
            'stateHooks': stateHooks,
            'conn': conn,
        }
        SearchClass = search_routes[
            (params.get('grouping'), bool(params.get('codes')))
        ]
        search = SearchClass(**init_params)
        #TODO: this is something GallicaGroupedSearch should take care of itself
        if isinstance(search, GallicaGroupedSearch):
            if search.more_date_intervals_than_record_batches() and len(args_for_tickets.items()) == 1:
                params['grouping'] = 'all'
                search = AllSearch(**init_params)
                stateHooks.onSearchChangeToAll(ticketID)
        search_objs.append(search)
    return search_objs

def all_volume_occurrence_search(args, requestID, ticketID, conn, onProgressUpdate):
    pass

def pyllica_search(args, requestID, ticketID, conn, onProgressUpdate):
    pass

def period_occurrence_search(args, requestID, ticketID, conn, onProgressUpdate):
    pass

#Components?
class AllSearch(SearchMixin):

    def __init__(self, input_args, requestID, onProgressUpdate, identifier, conn):
        self.args = input_args
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.conn = conn
        self.api = self.get_api_wrapper()
        self.base_queries_with_num_results = self.api.get_num_results_for_args(**self.args)
        self.insert_records = insert_records_into_results

    def get_total_records_to_insert(self, onNumRecordsFound):
        found = sum(queryWithResult[1] for queryWithResult in self.base_queries_with_num_results)
        onNumRecordsFound(self, found)
        return found

    def get_api_wrapper(self):
        return gallicaGetter.connect(
            gallicaAPIselect='sru',
            ticketID=self.identifier,
            requestID=self.stateHooks.requestID
        )

    def get_local_fetch_args(self):
        return {
            'queriesWithCounts': self.base_queries_with_num_results,
            'generate': True,
            'onUpdateProgress': lambda progressStats: self.stateHooks.setSearchProgressStats(
                progressStats={
                    **progressStats,
                    "ticketID": self.identifier
                }
            )
        }


class PyllicaSearch(SearchMixin):

    def __init__(self, input_args, identifier, stateHooks, conn):
        self.args = input_args
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.conn = conn
        self.api = pyllicaWrapper
        self.insert_records = insert_records_into_groupcounts
        self.total_records_to_insert = self.get_total_records_to_insert()
        self.stateHooks.setSearchProgressStats(
            progressStats={
                'ticketID': self.identifier,
                'totalRecords': self.total_records_to_insert,
                'insertedRecords': 0
            }
        )

    def get_total_records_to_insert(self, onNumRecordsFound=None):
        return get_num_periods_in_range_for_grouping(
            grouping=self.args['grouping'],
            start=self.args['startDate'],
            end=self.args['endDate']
        )

    def get_local_fetch_args(self):
        return {
            'ticketID': self.identifier,
            'requestID': self.stateHooks.requestID
        }


class GallicaGroupedSearch(Search):

    def get_api_wrapper(self):
        return gallicaGetter.connect(
            'sru',
            ticketID=self.identifier,
            requestID=self.stateHooks.requestID
        )

    def get_db_insert(self):
        return insert_records_into_groupcounts

    def get_total_records_to_insert(self, onNumRecordsFound=None):
        num_records = get_num_periods_in_range_for_grouping(
            grouping=self.args['grouping'],
            start=self.args['startDate'],
            end=self.args['endDate']
        )
        if onNumRecordsFound:
            onNumRecordsFound(self, num_records)
        return num_records

    def more_date_intervals_than_record_batches(self):
        args = {**self.args, 'grouping': 'all'}
        first_result = self.api.get_num_results_for_args(**args)[0]
        num_results = first_result[1]
        num_intervals = self.get_total_records_to_insert()
        return int(num_results / 50) < num_intervals

    def get_local_fetch_args(self):
        return {
            'onUpdateProgress': lambda progressStats: self.stateHooks.setSearchProgressStats(
                progressStats={
                    **progressStats,
                    "ticketID": self.identifier
                }
            )
        }


def get_num_periods_in_range_for_grouping(grouping, start, end) -> int:
    start, end = int(start), int(end)
    if grouping == 'year':
        return end - start + 1
    elif grouping == 'month':
        return (end - start + 1) * 12
    else:
        raise ValueError(f'Invalid grouping: {grouping}')
