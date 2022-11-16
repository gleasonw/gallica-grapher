from database.recordInsertResolvers import (
    insert_records_into_groupcounts,
    insert_records_into_results
)
import gallicaGetter
import appsearch.pyllicaWrapper as pyllicaWrapper


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
    searchObjs = []
    for ticketID, params in args_for_tickets.items():
        initParams = {
            'identifier': ticketID,
            'input_args': params,
            'stateHooks': stateHooks,
            'conn': conn,
        }
        SearchClass = search_routes[
            (params.get('grouping'), bool(params.get('codes')))
        ]
        searchObj = SearchClass(**initParams)
        if isinstance(searchObj, GallicaGroupedSearch):
            if searchObj.moreDateIntervalsThanRecordBatches() and len(args_for_tickets.items()) == 1:
                params['grouping'] = 'all'
                searchObj = AllSearch(**initParams)
                stateHooks.onSearchChangeToAll(ticketID)
        searchObjs.append(searchObj)
    return searchObjs


class Search:

    def __init__(self, input_args, stateHooks, identifier, conn):
        self.args = {
            **input_args,
            'startDate': input_args['startDate'],
            'endDate': input_args['endDate']
        }
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.conn = conn
        self.insertRecordsToDB = self.getDBinsert()
        self.api = self.getAPIWrapper()
        self.postInit()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.args})'

    def getRecordsFromAPIAndInsertToDB(self):
        return self.insertRecordsToDB(
            records=self.api.get(**self.buildAPIFetchArgs()),
            identifier=self.identifier,
            stateHooks=self.stateHooks,
            conn=self.conn
        )

    def getNumRecordsToBeInserted(self, onNumRecordsFound):
        raise NotImplementedError

    def getAPIWrapper(self):
        raise NotImplementedError

    def getDBinsert(self):
        raise NotImplementedError

    def buildAPIFetchArgs(self):
        self.args.update(self.getLocalFetchArgs())
        return self.args

    def postInit(self):
        pass

    def getLocalFetchArgs(self):
        return {}


class AllSearch(Search):

    def postInit(self):
        self.baseQueriesWithNumResults = self.api.getNumResultsForArgs(
            args={
                **self.args,
                'numRecords':1
            }
        )

    def getNumRecordsToBeInserted(self, onNumRecordsFound):
        found = sum(queryWithResult[1] for queryWithResult in self.baseQueriesWithNumResults)
        onNumRecordsFound(self, found)
        return found

    def getAPIWrapper(self):
        return gallicaGetter.connect(
            gallicaAPIselect='sru',
            ticketID=self.identifier,
            requestID=self.stateHooks.requestID
        )

    def getDBinsert(self):
        return insert_records_into_results

    def getLocalFetchArgs(self):
        return {
            'queriesWithCounts': self.baseQueriesWithNumResults,
            'generate': True,
            'onUpdateProgress': lambda progressStats: self.stateHooks.setSearchProgressStats(
                progressStats={
                    **progressStats,
                    "ticketID": self.identifier
                }
            )
        }


class PyllicaSearch(Search):

    def getAPIWrapper(self):
        return pyllicaWrapper

    def getDBinsert(self):
        return insert_records_into_groupcounts

    def getNumRecordsToBeInserted(self, onNumRecordsFound=None):
        return get_num_periods_in_range_for_grouping(
            grouping=self.args['grouping'],
            start=self.args['startDate'],
            end=self.args['endDate']
        )

    def getLocalFetchArgs(self):
        return {
            'ticketID': self.identifier,
            'requestID': self.stateHooks.requestID
        }


class GallicaGroupedSearch(Search):

    def getAPIWrapper(self):
        return gallicaGetter.connect(
            'sru',
            ticketID=self.identifier,
            requestID=self.stateHooks.requestID
        )

    def getDBinsert(self):
        return insert_records_into_groupcounts

    def getNumRecordsToBeInserted(self, onNumRecordsFound=None):
        num_records = get_num_periods_in_range_for_grouping(
            grouping=self.args['grouping'],
            start=self.args['startDate'],
            end=self.args['endDate']
        )
        if onNumRecordsFound:
            onNumRecordsFound(self, num_records)
        return num_records

    def moreDateIntervalsThanRecordBatches(self):
        args = {**self.args, 'grouping': 'all'}
        firstResult = self.api.getNumResultsForArgs(args)[0]
        numResults = firstResult[1]
        numIntervals = self.getNumRecordsToBeInserted()
        return int(numResults / 50) < numIntervals

    def getLocalFetchArgs(self):
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
