class RecordGetter:

    def __init__(
            self,
            gallicaAPI,
            parseData,
            onUpdateProgress=None
    ):
        self.gallicaAPI = gallicaAPI
        self.parseDataToRecords = parseData
        self.onUpdateProgress = onUpdateProgress

    def getFromQueries(self, queries):
        rawResponse = self.gallicaAPI.fetchAll(
            queries=queries,
            onUpdateProgress=self.onUpdateProgress
        )
        records = self.parseDataToRecords.parseResponsesToRecords(rawResponse)
        return records
