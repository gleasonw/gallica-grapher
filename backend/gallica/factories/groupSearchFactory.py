from gallica.search import Search
from gallica.recordGetter import RecordGetter


class GroupSearchFactory:

    def __init__(
            self,
            ticket,
            onProgressUpdate,
            dbLink,
            parse,
            baseQueries,
            requestID,
            onUpdateProgress,
            sruFetcher,
            onAddingResultsToDB
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.onProgressUpdate = onProgressUpdate
        self.insertIntoGroupCounts = dbLink.insertRecordsIntoGroupCounts
        self.parser = ParseGroupedRecordCounts(parse)
        self.buildQueries = baseQueries.build
        self.onUpdateProgress = onUpdateProgress
        self.sruFetcher = sruFetcher
        self.onAddingResultsToDB = onAddingResultsToDB

    def getSearch(self):
        queries = self.buildQueries(
            self.ticket,
            self.ticket.getGroupingIntervals()
        )
        return Search(
            queries=queries,
            insertRecordsIntoDatabase=self.insertIntoGroupCounts,
            recordGetter=RecordGetter(
                gallicaAPI=self.sruFetcher,
                parseData=self.parser,
                onUpdateProgress=self.onUpdateProgress
            ),
            onAddingResultsToDB=self.onAddingResultsToDB
        )


class ParseGroupedRecordCounts:

    def __init__(self, parser):
        self.parser = parser

    def parse(self, xml):
        return self.parser.numRecords(xml)
