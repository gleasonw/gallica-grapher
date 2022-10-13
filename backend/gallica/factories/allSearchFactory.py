from gallica.factories.queryIndexer import QueryIndexer
from gallica.fetchComponents.query import Query
from gallica.search import Search
from gallica.recordGetter import RecordGetter
from gallica.dto.occurrenceRecord import OccurrenceRecord


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
            onAddingMissingPapersToDB
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.insertIntoResults = dbLink.insertRecordsIntoResults
        self.parse = ParseOccurrenceRecords(
            parser=parse,
            ticketID=ticket.getID(),
            requestID=requestID
        )
        self.buildQueriesForTicket = queryBuilder.buildForTicket
        self.onUpdateProgress = onUpdateProgress
        self.sruFetcher = sruFetcher
        self.onAddingResultsToDB = onAddingResultsToDB
        self.queryIndexer = QueryIndexer(
            gallicaAPI=self.sruFetcher,
            parse=parse,
            makeQuery=Query
        )
        self.getNumResultsForEachQuery = self.queryIndexer.getNumResultsForEachQuery
        self.makeIndexedQueriesForEachBaseQuery = self.queryIndexer.makeIndexedQueries
        self.onAddingMissingPapers = onAddingMissingPapersToDB

    def getSearch(self):
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
                'onAddingMissingPapers': self.onAddingMissingPapers
            },
            numRecordsToFetch=sum(
                [numResults for numResults in queriesWithNumResults.values()]
            ),
            searchType=self.ticket.getSearchType(),
            ticketID=self.ticket.getID()
        )


class ParseOccurrenceRecords:

    def __init__(self, parser, requestID, ticketID):
        self.parser = parser
        self.requestID = requestID
        self.ticketID = ticketID

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generateOccurrenceRecords(
                query=response.query,
                xml=response.xml
            )

    def generateOccurrenceRecords(self, xml, query):
        for record in self.parser.getRecordsFromXML(xml):
            paperTitle = self.parser.getPaperTitleFromRecord(record)
            paperCode = self.parser.getPaperCodeFromRecord(record)
            date = self.parser.getDateFromRecord(record)
            yield OccurrenceRecord(
                paperTitle=paperTitle,
                paperCode=paperCode,
                date=date,
                url=self.parser.getURLfromRecord(record),
                term=query.term,
                requestID=self.requestID,
                ticketID=self.ticketID
            )

