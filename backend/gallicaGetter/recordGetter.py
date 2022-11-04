class RecordGetter:

    def __init__(
            self,
            gallicaAPI,
            parseData,
    ):
        self.gallicaAPI = gallicaAPI
        self.parser = parseData

    def getFromQueries(self, queries, onUpdateProgress=None):
        rawResponse = self.gallicaAPI.get(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        records = self.parser.parseResponsesToRecords(rawResponse)
        return records


