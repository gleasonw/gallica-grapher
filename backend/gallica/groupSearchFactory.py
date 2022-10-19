from gallica.search import Search
from recordGetter import RecordGetter


class GroupSearchFactory:

    def __init__(
            self,
            ticket,
            onUpdateProgress,
            dbLink,
            parse,
            requestID,
            sruFetcher,
            queryBuilder,
            onAddingResultsToDB,
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.onUpdateProgress = onUpdateProgress
        self.insertIntoGroupCounts = dbLink.insertRecordsIntoGroupCounts
        self.parser = ParseGroupedRecordCounts(
            parser=parse,
            ticketID=ticket.getID(),
            requestID=requestID
        )
        self.buildQueriesForTicket = queryBuilder.buildForBundle
        self.onUpdateProgress = onUpdateProgress
        self.sruFetcher = sruFetcher
        self.onAddingResultsToDB = onAddingResultsToDB

    def prepare(self, request):
        queries = self.buildQueriesForTicket(self.ticket)
        return Search(
            queries=queries,
            insertRecordsIntoDatabase=self.insertIntoGroupCounts,
            recordGetter=RecordGetter(
                gallicaAPI=self.sruFetcher,
                parseData=self.parser,
                onUpdateProgress=self.onUpdateProgress
            ),
            requestStateHandlers={
                'onAddingResultsToDB': self.onAddingResultsToDB
            },
            numRecordsToFetch=len(queries),
            ticketID=self.ticket.getID()
        )


