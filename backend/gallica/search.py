class Search:

    def __init__(
            self,
            queries,
            gallicaAPI,
            onUpdateProgress,
            insertRecordsIntoDatabase,
            parseDataToRecords
    ):
        self.queries = queries
        self.gallicaAPI = gallicaAPI
        self.onUpdateProgress = onUpdateProgress
        self.insertRecordsIntoDatabase = insertRecordsIntoDatabase
        self.parseDataToRecords = parseDataToRecords

    def run(self):
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
