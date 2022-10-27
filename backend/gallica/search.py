from dbops.schemaLinkForSearch import SchemaLinkForSearch
import gallica.gallicaWrapper as gallicaWrapper


def build(argBundles, stateHooks):
    searches = {
        'all': AllSearch,
        'year': GroupedSearch,
        'month': GroupedSearch
    }
    searchObjs = []
    for key, bundle in argBundles.items():
        search = bundle['grouping']
        runner = searches[search](
            identifier=key,
            stateHooks=stateHooks,
            args=bundle
        )
        if search != 'all' and runner.moreDateIntervalsThanRecordBatches() and len(argBundles.items()) == 1:
            bundle['grouping'] = 'all'
            runner = AllSearch(
                identifier=key,
                stateHooks=stateHooks,
                args=bundle
            )
            stateHooks.onSearchChangeToAll(key)
        searchObjs.append(runner)
    return searchObjs


class Search:

    def __init__(self, identifier, stateHooks, args):
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.args = args
        self.args['startDate'] = int(self.args['startDate'])
        self.args['endDate'] = int(self.args['endDate'])
        self.dbLink = SchemaLinkForSearch(requestID=stateHooks.requestID)
        self.insertRecordsToDB = self.getDBinsert()
        self.api = self.getAPIWrapper(
            ticketID=self.identifier,
            requestID=stateHooks.requestID
        )
        self.postInit()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.args})'

    def getRecordsFromAPIAndInsertToDB(self):
        records = self.api.get(**self.buildAPIFetchArgs())
        return self.insertRecordsToDB(
            records=records,
            identifier=self.identifier,
            stateHooks=self.stateHooks
        )

    def getNumRecordsToBeInserted(self, onNumRecordsFound):
        raise NotImplementedError

    def getAPIWrapper(self, ticketID, requestID):
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

    def getAPIWrapper(self, ticketID, requestID):
        return gallicaWrapper.connect(
            gallicaAPIselect='sru',
            ticketID=ticketID,
            requestID=requestID
        )

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoResults

    def getLocalFetchArgs(self):
        return {
            'queriesWithCounts': self.baseQueriesWithNumResults,
            'generate': True
        }


class GroupedSearch(Search):

    def getAPIWrapper(self, ticketID, requestID):
        return gallicaWrapper.connect(
            gallicaAPIselect='sru',
            ticketID=ticketID,
            requestID=requestID
        )

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoGroupCounts

    def getNumRecordsToBeInserted(self, onNumRecordsFound=None):
        startDate = self.args.get('startDate')
        endDate = self.args.get('endDate')
        grouping = self.args.get('grouping')
        if grouping == 'year':
            sum = endDate + 1 - startDate
        else:
            sum = (endDate + 1 - startDate) * 12
        onNumRecordsFound and onNumRecordsFound(self, sum)
        return sum

    def moreDateIntervalsThanRecordBatches(self):
        args = {**self.args, 'grouping': 'all'}
        numResults = self.api.getNumResultsForArgs(args)[0][1]
        numIntervals = self.getNumRecordsToBeInserted()
        return int(numResults / 50) < numIntervals


class PaperSearch(Search):

    def getAPIWrapper(self):
        return gallicaWrapper.connect('papers')

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoPapers



