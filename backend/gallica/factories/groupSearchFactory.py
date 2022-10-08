from gallica.search import Search

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
            onSearchFinish,
            sruFetcher
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.onProgressUpdate = onProgressUpdate
        self.insertIntoGroupCounts = dbLink.insertRecordsIntoGroupCounts
        self.parse = parse.numRecords
        self.buildQueries = baseQueries.build
        self.onUpdateProgress = onUpdateProgress
        self.onSearchFinish = onSearchFinish
        self.sruFetcher = sruFetcher

    def getGroupSearch(self):
        queries = self.buildQueries(
            self.ticket,
            self.ticket.getGroupingIntervals()
        )
        return Search(
            ticketID=self.ticket.getID(),
            requestID=self.requestID,
            queries=queries,
            SRUfetch=self.sruFetcher,
            parseDataToRecords=self.parse,
            insertRecordsIntoDatabase=self.insertIntoGroupCounts,
            onUpdateProgress=self.onUpdateProgress,
            onSearchFinish=self.onSearchFinish,
            numRecords=len(queries)
        )
