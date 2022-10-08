from fetchComponents import Query


class QueryFactory:

    def __init__(self, sruFetcher):
        self.sruFetcher = sruFetcher

    def build(self, ticket, startEndDates):
        for term in ticket.getTerms():
            for dates in startEndDates:
                if codeBundles := ticket.getCodeBundles():
                    return [
                        self.makeQuery(
                            term=term,
                            ticket=ticket,
                            dates=dates,
                            codes=codes
                        )
                        for codes in codeBundles
                    ]
                else:
                    return [
                        self.makeQuery(
                            term=term,
                            ticket=ticket,
                            dates=dates
                        )
                    ]

    def makeQuery(self, term, ticket, dates, codes=[]):
        return Query(
            term=term,
            publicationStartDate=dates[0],
            publicationEndDate=dates[1],
            linkTerm=ticket.getLinkTerm(),
            linkDistance=ticket.getLinkDistance(),
            startIndex=0,
            numRecords=1,
            collapsing=False,
            codes=codes
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
