class QueryIndexer:

    def __init__(self, gallicaAPI, parse, makeQuery):
        self.gallicaAPI = gallicaAPI
        self.parse = parse
        self.makeQuery = makeQuery

    def getNumResultsForEachQuery(self, queries) -> dict:
        responses = self.gallicaAPI.fetchAll(queries)
        numResultsForQueries = {}
        for response in responses:
            numRecordsForBaseCQL = self.parse.getNumRecords(response.xml)
            numResultsForQueries[response.query] = numRecordsForBaseCQL
        return numResultsForQueries

    def makeIndexedQueries(self, baseQueries) -> list:
        indexedQueries = []
        for query, numResults in baseQueries.items():
            for i in range(0, numResults, 50):
                baseData = query.getEssentialDataForMakingAQuery()
                baseData["startIndex"] = i
                baseData["getNumRecords"] = 50
                indexedQueries.append(
                    self.makeQuery(**baseData)
                )
        return indexedQueries
