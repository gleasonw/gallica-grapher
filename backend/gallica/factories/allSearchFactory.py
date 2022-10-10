from lxml import etree
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
        self.parse = ParseOccurrenceRecords(parse)
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

#TODO: pass ticket down, add metadatd to OccurrenceRecord
class ParseOccurrenceRecords:

    def __init__(self, parser):
        self.parser = parser

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generateOccurrenceRecords(response.xml)

    def generateOccurrenceRecords(self, xml):
        elements = etree.fromstring(xml)
        if elements.find("{http://www.loc.gov/zing/srw/}records") is None:
            return []
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.parser.getDataFromRecordRoot(record)
            paperTitle = self.parser.getPaperTitle(data)
            paperCode = self.parser.getPaperCode(data)
            date = self.parser.getDate(data)
            newRecord = OccurrenceRecord(
                paperTitle=paperTitle,
                paperCode=paperCode,
                date=date,
                url=self.parser.getURL(data),
            )
            yield newRecord
