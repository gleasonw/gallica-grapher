from gallica.search import Search
from gallica.recordGetter import RecordGetter
from gallica.dto.groupedCountRecord import GroupedCountRecord


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
        self.parser = ParseGroupedRecordCounts(
            parser=parse,
            ticketID=ticket.getID(),
            requestID=requestID
        )
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
            onAddingResultsToDB=self.onAddingResultsToDB,
            numRecordsToFetch=len(queries)
        )


class ParseGroupedRecordCounts:

    def __init__(self, parser, ticketID, requestID):
        self.parser = parser
        self.ticketID = ticketID
        self.requestID = requestID

    def parseResponsesToRecords(self, responses):
        for response in responses:
            count = self.parser.numRecords(response.xml)
            query = response.query
            yield GroupedCountRecord(
                date=query.getStartDate(),
                count=count,
                ticketID=self.ticketID,
                term=query.term,
                requestID=self.requestID
            )