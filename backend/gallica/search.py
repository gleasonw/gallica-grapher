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
        self.params['startDate'] = int(self.params['startDate'])
        self.params['endDate'] = int(self.params['endDate'])
        self.dbLink = SchemaLinkForSearch(requestID=stateHooks.requestID)
        self.insertRecordsToDB = self.getDBinsert()
        self.api = self.getAPIWrapper(
            ticketID=self.identifier,
            requestID=stateHooks.requestID
        )
        self.postInit()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.params})'

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
            **self.params
        }
        baseArgs.update(self.getLocalFetchArgs())
        return baseArgs

    def postInit(self):
        pass

    def getLocalFetchArgs(self):
        return {}


class AllSearch(Search):

    def postInit(self):
        self.baseQueriesWithNumResults = self.api.getNumRecordsForArgs(**self.params)

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

    def getNumRecordsToBeInserted(self, onNumRecordsFound):
        startDate = self.params.get('startDate')
        endDate = self.params.get('endDate')
        grouping = self.params.get('grouping')
        if grouping == 'year':
            sum = endDate + 1 - startDate
        else:
            sum = (endDate + 1 - startDate) * 12
        onNumRecordsFound(self, sum)
        return sum


class PaperSearch(Search):

    def getAPIWrapper(self):
        return gallicaWrapper.connect('papers')

    def getDBinsert(self):
        return self.dbLink.insertRecordsIntoPapers



