from dbops.schemaLinkForSearch import SchemaLinkForSearch
import gallica.gallicaWrapper as gallicaWrapper


def build(argBundles, stateHooks, wrapper=gallicaWrapper):
    searches = {
        'all': AllSearch,
        'year': GroupedSearch,
        'month': GroupedSearch
    }
    searchObjs = []
    for key, bundle in argBundles.items():
        initParams = {
            'identifier': key,
            'args': bundle,
            'stateHooks': stateHooks,
            'connectable': wrapper
        }
        search = bundle['grouping']
        runner = searches[search](**initParams)
        if search != 'all' and runner.moreDateIntervalsThanRecordBatches() and len(argBundles.items()) == 1:
            bundle['grouping'] = 'all'
            runner = AllSearch(**initParams)
            stateHooks.onSearchChangeToAll(key)
        searchObjs.append(runner)
    return searchObjs


class Search:

    def __init__(self, identifier, stateHooks, args, connectable):
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.args = {
            **args,
            'startDate': int(args['startDate']),
            'endDate': int(args['endDate'])
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

    def getAPIWrapper(self, wrapper):
        return wrapper.connect(
            gallicaAPIselect='sru',
            ticketID=self.identifier,
            requestID=self.stateHooks.requestID
        )

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoGroupCounts

    def getNumRecordsToBeInserted(self, onNumRecordsFound=None):
        numRecords = self.args['endDate'] + 1 - self.args['startDate']
        if self.args['grouping'] == 'month':
            numRecords *= 12
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



