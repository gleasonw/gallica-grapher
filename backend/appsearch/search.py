from database.recordInsertResolvers import (
    insert_records_into_groupcounts,
    insert_records_into_results
)
import gallicaGetter
import appsearch.pyllicaWrapper as pyllicaWrapper


def get_and_insert_records_for_args(ticketID, args, onProgressUpdate):
    pass


def all_volume_occurrence_search(
        args,
        requestID,
        ticketID,
        conn,
        onProgressUpdate):
    pass


def pyllica_search(
        args,
        requestID,
        ticketID,
        conn,
        onProgressUpdate,
        onNumResultFound
):
    api = gallicaGetter.connect(
        gallicaAPIselect='volume',
        ticketID=ticketID,
        requestID=requestID,
    )
    base_queries_with_num_results = api.get_num_results_for_args(**args)
    total_records_to_insert = sum(query.num_results for query in base_queries_with_num_results)
    onNumResultFound(total_records_to_insert)


def period_occurrence_search(
        args,
        requestID,
        ticketID,
        conn,
        onProgressUpdate):
    pass

    # Components?
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


