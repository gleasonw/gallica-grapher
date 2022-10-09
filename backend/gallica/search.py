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
        records = self.parseDataToRecords(rawResponse)
        return self.insertRecordsIntoDatabase(records)