from dbops.schemaLinkForSearch import SchemaLinkForSearch
import gallicaWrapper


def build(argBundles, stateHooks):
    searches = {
        'all': AllSearch,
        'year': GroupedSearch,
        'month': GroupedSearch
    }
    searchObjs = []
    for key, bundle in argBundles.items():
        search = bundle['grouping']
        searchObjs.append(searches[search](
            identifier=key,
            stateHooks=stateHooks,
            args=bundle
        ))
    return searchObjs


class Search:

    def __init__(self, identifier, stateHooks, args):
        self.identifier = identifier
        self.stateHooks = stateHooks
        self.params = args
        self.dbLink = SchemaLinkForSearch(requestID=args.get('requestID'))
        self.insertRecordsToDB = self.getDBinsert()
        self.api = self.getAPIWrapper()
        self.postInit()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.params})'

    def getRecordsFromAPIAndInsertToDB(self):
        records = self.api.get(**self.buildAPIFetchArgs())
        return self.insertRecordsToDB(
            records=records,
            stateHooks=self.stateHooks
        )

    def getNumRecordsToBeInserted(self):
        raise NotImplementedError

    def getAPIWrapper(self):
        raise NotImplementedError

    def getDBinsert(self):
        raise NotImplementedError

    def buildAPIFetchArgs(self):
        baseArgs= {'onUpdateProgress': lambda progressStats: self.stateHooks.setProgressStats(
            progressStats=progressStats,
            ticketID=self.params.get('ticketID'),
        )}
        baseArgs.update(self.getLocalFetchArgs())
        return baseArgs

    def postInit(self):
        pass

    def getLocalFetchArgs(self):
        return {}


class AllSearch(Search):

    def postInit(self):
        self.baseQueriesWithNumResults = self.api.getNumRecordsForArgs(**self.params)

    def getNumRecordsToBeInserted(self):
        return sum(queryWithResult[1] for queryWithResult in self.baseQueriesWithNumResults)

    def getAPIWrapper(self):
        return gallicaWrapper.connect('sru')

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoResults

    def getLocalFetchArgs(self):
        return {
            'queriesWithCounts': self.baseQueriesWithNumResults,
            'generate': True
        }


class GroupedSearch(Search):

    def getAPIWrapper(self):
        return gallicaWrapper.connect('sru')

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoGroupCounts

    def getNumRecordsToBeInserted(self):
        startYear = self.params.get('startDate')
        endYear = self.params.get('endDate')
        grouping = self.params.get('grouping')
        if grouping == 'year':
            return endYear + 1 - startYear
        else:
            return (endYear + 1 - startYear) * 12


class PaperSearch(Search):

    def getAPIWrapper(self):
        return gallicaWrapper.connect('papers')

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoPapers



