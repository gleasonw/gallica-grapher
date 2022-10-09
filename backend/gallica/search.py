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
        records = self.parseDataToRecords(rawResponse)
        return self.insertRecordsIntoDatabase(records)