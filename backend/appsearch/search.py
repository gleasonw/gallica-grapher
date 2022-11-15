from dbops.insertRecordsOps import (
    insertRecordsIntoGroupCounts,
    insertRecordsIntoResults,
)
import gallicaGetter
import appsearch.pyllicaWrapper as pyllicaWrapper


def buildSearch(argBundles, stateHooks, wrapper=gallicaGetter):
    searches = {
        'all': AllSearch,
        'year': GroupedSearch,
        'month': GroupedSearch
    }
    searchObjs = []
    for key, bundle in argBundles.items():
        search = bundle.get('grouping')
        api = wrapper if search == 'all' else pyllicaWrapper
        initParams = {
            'identifier': key,
            'input_args': bundle,
            'stateHooks': stateHooks,
            'connectable': api
        }
        runner = searches[search](**initParams)
        searchObjs.append(runner)
    return searchObjs


class Search:

    def __init__(self, input_args, connectable, stateHooks, identifier):
        self.args = {
            **input_args,
            'startDate': input_args['startDate'],
            'endDate': input_args['endDate']
        }
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.insertRecordsToDB = self.getDBinsert()
        self.api = self.getAPIWrapper(connectable)
        self.postInit()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.args})'

    def getRecordsFromAPIAndInsertToDB(self):
        return self.insertRecordsToDB(
            records=self.api.get(**self.buildAPIFetchArgs()),
            identifier=self.identifier,
            stateHooks=self.stateHooks
        )

    def getNumRecordsToBeInserted(self, onNumRecordsFound):
        raise NotImplementedError

    def getAPIWrapper(self, wrapper):
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

    def getAPIWrapper(self, wrapper):
        return wrapper.connect(
            gallicaAPIselect='sru',
            ticketID=self.identifier,
            requestID=self.stateHooks.requestID
        )

    def getDBinsert(self):
        return insertRecordsIntoResults

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


class GroupedSearch(Search):

    def getAPIWrapper(self, connectable):
        return connectable

    def getDBinsert(self):
        return insertRecordsIntoGroupCounts

    def getNumRecordsToBeInserted(self, onNumRecordsFound=None):
        numRecords = 5
        onNumRecordsFound and onNumRecordsFound(self, numRecords)
        return numRecords

    def getLocalFetchArgs(self):
        return {
            'ticketID': self.identifier,
            'requestID': self.stateHooks.requestID
        }
