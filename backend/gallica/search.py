class Search:

    def __init__(
            self,
            ticketID,
            requestID,
            queries,
            SRUfetch,
            onUpdateProgress,
            insertRecordsIntoDatabase,
            onSearchFinish,
            parseDataToRecords,
            getEstimateNumRecordsToFetch
    ):
        self.ticketID = ticketID
        self.requestID = requestID
        self.queries = queries
        self.SRUfetch = SRUfetch
        self.onUpdateProgress = onUpdateProgress
        self.insertRecordsIntoDatabase = insertRecordsIntoDatabase
        self.onSearchFinish = onSearchFinish
        self.parseDataToRecords = parseDataToRecords
        self.getEstimateNumRecordsToFetch = getEstimateNumRecordsToFetch

    def getTicketID(self):
        return self.ticketID

    def getEstimateNumRecords(self):
        return self.getEstimateNumRecordsToFetch(self.queries)

    def doSearch(self):
        rawResponse = self.getSearchResponse()
        records = self.parseSearchResponse(rawResponse)
        return self.insertRecordsIntoDatabase(records)

    def getSearchResponse(self):
        return self.SRUfetch(
            self.queries,
            self.onUpdateProgress
        )

    def parseSearchResponse(self, rawResponse):
        for data, query in rawResponse:
            records = self.parseDataToRecords(data)
            for record in records:
                record.addFinalRowElements(
                    ticketID=self.ticketID,
                    requestID=self.requestID,
                    term=query.term
                )
                yield record
