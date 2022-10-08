from parseOccurrenceRecords import ParseOccurrenceRecords
from gallica.search import Search


class AllSearchFactory:

    def __init__(
            self,
            ticket,
            dbLink,
            baseQueries,
            requestID,
            parse,
            onUpdateProgress,
            sruFetcher
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.insertIntoResults = dbLink.insertRecordsIntoResults
        self.parse = ParseOccurrenceRecords(parse)
        self.buildQueries = baseQueries.build
        self.getNumResultsForEachQuery = baseQueries.getNumResultsForEachQuery
        self.makeIndexedQueriesForEachBaseQuery = baseQueries.makeIndexedQueriesForEachBaseQuery
        self.onUpdateProgress = onUpdateProgress
        self.sruFetcher = sruFetcher

    def getSearch(self):
        queries = self.buildQueries(
            self.ticket,
            [(self.ticket.getStartDate(), self.ticket.getEndDate())]
        )
        queriesWithNumResults = self.getNumResultsForEachQuery(queries)
        return Search(
            queries=self.makeIndexedQueriesForEachBaseQuery(
                queriesWithNumResults),
            gallicaAPI=self.sruFetcher,
            parseDataToRecords=self.parse,
            insertRecordsIntoDatabase=self.insertIntoResults,
            onUpdateProgress=self.onUpdateProgress,
        )
