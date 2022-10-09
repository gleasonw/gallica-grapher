class Search:

    def __init__(
            self,
            queries,
            gallicaAPI,
            onUpdateProgress,
            insertRecordsIntoDatabase,
            parseDataToRecords,
            recordGetter
    ):
        self.queries = queries
        self.gallicaAPI = gallicaAPI
        self.onUpdateProgress = onUpdateProgress
        self.insertRecordsIntoDatabase = insertRecordsIntoDatabase
        self.parseDataToRecords = parseDataToRecords
        self.recordGetter = recordGetter

    def run(self):
        #TODO: Implement:
        records = self.recordGetter.getFromQueries(queries)
        rawResponse = self.gallicaAPI.api(
            queries=self.queries,
            onUpdateProgress=self.onUpdateProgress
        )
        records = self.parseSearchResponse(rawResponse)
        return self.insertRecordsIntoDatabase(records)

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
