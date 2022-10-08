class QueryIndexer:

    def __init__(self, gallicaAPI, parse, makeQuery):
        self.gallicaAPI = gallicaAPI
        self.parse = parse
        self.makeQuery = makeQuery

    def getNumResultsForEachQuery(self, queries) -> dict:
        responses = self.gallicaAPI.fetchAll(queries)
        numResultsForQueries = {}
        for data, query in responses:
            numRecordsForBaseCQL = self.parse.numRecords(data)
            numResultsForQueries[query] = numRecordsForBaseCQL
        return numResultsForQueries

    def makeIndexedQueriesForEachBaseQuery(self, baseQueries) -> list:
        indexedQueries = []
        for query, numResults in baseQueries.items():
            for i in range(0, numResults, 50):
                baseData = query.getEssentialDataForMakingAQuery()
                baseData["startIndex"] = i
                baseData["numRecords"] = 50
                indexedQueries.append(self.makeQuery(baseData))
        return indexedQueries
