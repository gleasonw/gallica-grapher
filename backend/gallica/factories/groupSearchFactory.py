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
            sruFetcher
    ):
        self.requestID = requestID
        self.ticket = ticket
        self.onProgressUpdate = onProgressUpdate
        self.insertIntoGroupCounts = dbLink.insertRecordsIntoGroupCounts
        self.parse = parse.numRecords
        self.buildQueries = baseQueries.build
        self.onUpdateProgress = onUpdateProgress
        self.sruFetcher = sruFetcher

    def getSearch(self):
        queries = self.buildQueries(
            self.ticket,
            self.ticket.getGroupingIntervals()
        )
        return Search(
            queries=queries,
            gallicaAPI=self.sruFetcher,
            parseDataToRecords=self.parse,
            insertRecordsIntoDatabase=self.insertIntoGroupCounts,
            onUpdateProgress=self.onUpdateProgress,
        )
