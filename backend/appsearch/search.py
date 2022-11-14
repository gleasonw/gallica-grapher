from dbops.schemaLinkForSearch import SchemaLinkForSearch
import gallicaGetter
import pyllicaWrapper


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
            'args': bundle,
            'stateHooks': stateHooks,
            'connectable': api
        }
        runner = searches[search](**initParams)
        searchObjs.append(runner)
    return searchObjs


class Search:

    def __init__(self, identifier, stateHooks, args, connectable):
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.args = {
            **args,
            'startDate': args['startDate'],
            'endDate': args['endDate']
        }
        self.dbLink = SchemaLinkForSearch(requestID=stateHooks.requestID)
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
        baseArgs= {
            'onUpdateProgress': lambda progressStats: self.stateHooks.setSearchProgressStats(
                progressStats={
                    **progressStats,
                    "ticketID": self.identifier
                }
            ),
            **self.args
        }
        baseArgs.update(self.getLocalFetchArgs())
        return baseArgs

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
        return self.dbLink.insertRecordsIntoResults

    def getLocalFetchArgs(self):
        return {
            'queriesWithCounts': self.baseQueriesWithNumResults,
            'generate': True
        }


class GroupedSearch(Search):

    def getAPIWrapper(self, connectable):
        return connectable

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoGroupCounts

    def getNumRecordsToBeInserted(self, onNumRecordsFound=None):
        numRecords = 0
        onNumRecordsFound and onNumRecordsFound(self, numRecords)
        return numRecords

    def moreDateIntervalsThanRecordBatches(self):
        args = {**self.args, 'grouping': 'all'}
        firstResult = self.api.getNumResultsForArgs(args)[0]
        numResults = firstResult[1]
        numIntervals = self.getNumRecordsToBeInserted()
        return int(numResults / 50) < numIntervals


class PaperSearch(Search):

    def getAPIWrapper(self, wrapper):
        return wrapper.connect('papers')

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoPapers



