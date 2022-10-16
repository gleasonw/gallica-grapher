from queryIndexer import QueryIndexer
from query import TicketQuery
from gallica.search import Search
from recordGetter import RecordGetter
from parseOccurrenceRecords import ParseOccurrenceRecords


class AllSearchFactory:

    def __init__(
            self,
            ticket,
            dbLink,
            requestID,
            parse,
            onUpdateProgress,
            sruFetcher,
            queryBuilder,
            onAddingResultsToDB,
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.insertIntoResults = dbLink.insertRecordsIntoResults
        self.parse = ParseOccurrenceRecords(
            parser=parse,
            ticketID=ticket.getID(),
            requestID=requestID
        )
        self.buildQueriesForTicket = queryBuilder.buildForBundle
        self.onUpdateProgress = onUpdateProgress
        self.sruFetcher = sruFetcher
        self.onAddingResultsToDB = onAddingResultsToDB
        self.queryIndexer = QueryIndexer(
            gallicaAPI=self.sruFetcher,
            parse=parse,
            makeQuery=TicketQuery
        )
        self.getNumResultsForEachQuery = self.queryIndexer.getNumResultsForEachQuery
        self.makeIndexedQueriesForEachBaseQuery = self.queryIndexer.makeIndexedQueries

    def prepare(self, request):
        queries = self.buildQueriesForTicket(self.ticket)
        queriesWithNumResults = self.getNumResultsForEachQuery(queries)
        return Search(
            queries=self.makeIndexedQueriesForEachBaseQuery(
                queriesWithNumResults),
            insertRecordsIntoDatabase=self.insertIntoResults,
            recordGetter=RecordGetter(
                gallicaAPI=self.sruFetcher,
                parseData=self.parse,
                onUpdateProgress=self.onUpdateProgress
            ),
            requestStateHandlers={
                'onAddingResultsToDB': self.onAddingResultsToDB,
                'onAddingMissingPapers': lambda: request.setSearchState(
                    state='ADDING_MISSING_PAPERS',
                    ticketID=self.ticket.getID()
                )
            },
            numRecordsToFetch=sum(
                [numResults for numResults in queriesWithNumResults.values()]
            ),
            ticketID=self.ticket.getID()
        )


