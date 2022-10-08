from query import Query


class QueryFactory:

    def __init__(self, sruFetcher):
        self.sruFetcher = sruFetcher

    def build(self, ticket, startEndDates):
        for term in ticket.getTerms():
            for dates in startEndDates:
                queryData = {
                    "term":term,
                    "publicationStartDate":dates[0],
                    "publicationEndDate":dates[1],
                    "collapsing":False,
                    "numRecords":1,
                    "startIndex":0,
                }
                if codeBundles := ticket.getCodeBundles():
                    queries = []
                    for codes in codeBundles:
                        queryData['codes'] = codes
                        queries.append(self.makeQuery(queryData))
                    return queries
                else:
                    return [self.makeQuery(queryData)]

    def makeQuery(self, data):
        return Query(
            codes=data.get('codes'),
            linkDistance=data.get('linkDistance'),
            linkTerm=data.get('linkTerm'),
            publicationStartDate=data.get('publicationStartDate'),
            publicationEndDate=data.get('publicationEndDate'),
            term=data.get('term'),
            numRecords=data.get('numRecords'),
            startIndex=data.get('startIndex'),
            collapsing=data.get('collapsing')
        )

    def getNumResultsForEachQuery(self, queries) -> dict:
        responses = self.sruFetcher.fetchAll(queries)
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
                baseData["collapsing"] = False
                indexedQueries.append(self.makeQuery(baseData))
        return indexedQueries
