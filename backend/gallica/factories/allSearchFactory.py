from gallica.search import Search


class AllSearchFactory:

    def __init__(
            self,
            ticket,
            dbLink,
            parse,
            baseQueries,
            requestID,
            onUpdateProgress,
            onSearchFinish,
            sruFetcher
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.insertIntoResults = dbLink.insertRecordsIntoResults
        self.parse = parse.occurrences
        self.buildQueries = baseQueries.build
        self.getNumResultsForEachQuery = baseQueries.getNumResultsForEachQuery
        self.makeIndexedQueriesForEachBaseQuery = baseQueries.makeIndexedQueriesForEachBaseQuery
        self.onUpdateProgress = onUpdateProgress
        self.onSearchFinish = onSearchFinish
        self.sruFetcher = sruFetcher

    def getAllSearch(self):
        queries = self.buildQueries(
            self.ticket,
            [(self.ticket.getStartDate(), self.ticket.getEndDate())]
        )
        numResultsForQueries = self.getNumResultsForEachQuery(queries)
        numRecords = sum(numResultsForQueries.values())
        indexedQueries = self.makeIndexedQueriesForEachBaseQuery(queries)
        return Search(
            ticketID=self.ticket.getID(),
            requestID=self.requestID,
            queries=indexedQueries,
            SRUfetch=self.sruFetcher,
            parseDataToRecords=self.parse,
            insertRecordsIntoDatabase=self.insertIntoResults,
            onUpdateProgress=self.onUpdateProgress,
            onSearchFinish=self.onSearchFinish,
            numRecords=numRecords
        )
