from gallica.search import Search
from gallica.recordGetter import RecordGetter
from occurrenceRecord import OccurrenceRecord


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
            onAddingResultsToDB
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.insertIntoResults = dbLink.insertRecordsIntoResults
        self.parse = ParseOccurrenceRecords(
            parser=parse,
            ticketID=ticket.getID(),
            requestID=requestID
        )
        self.baseQueryBuilder = queryBuilder.build
        self.getNumResultsForEachQuery = queryBuilder.getNumResultsForEachQuery
        self.makeIndexedQueriesForEachBaseQuery = queryBuilder.makeIndexedQueries
        self.onUpdateProgress = onUpdateProgress
        self.sruFetcher = sruFetcher
        self.onAddingResultsToDB = onAddingResultsToDB

    def getSearch(self):
        queries = self.baseQueryBuilder(
            self.ticket,
            [(self.ticket.getStartDate(), self.ticket.getEndDate())]
        )
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
            onAddingResultsToDB=self.onAddingResultsToDB,
            numRecordsToFetch=sum(
                [numResults for numResults in queriesWithNumResults.values()]
            )
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
            data = self.parser.getDataFromRecordRoot(record)
            paperTitle = self.parser.getPaperTitle(data)
            paperCode = self.parser.getPaperCode(data)
            date = self.parser.getDate(data)
            yield OccurrenceRecord(
                paperTitle=paperTitle,
                paperCode=paperCode,
                date=date,
                url=self.parser.getURL(data),
                term=query.term,
                requestID=self.requestID,
                ticketID=self.ticketID
            )

