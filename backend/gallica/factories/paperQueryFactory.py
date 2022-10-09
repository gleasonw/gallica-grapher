from fetchComponents.query import ArkQueryForNewspaperYears
from fetchComponents.query import PaperQuery
from queryIndexer import QueryIndexer


class PaperQueryFactory:

    def __init__(self, gallicaAPI, parse):
        self.indexer = QueryIndexer(
            gallicaAPI=gallicaAPI,
            parse=parse,
            makeQuery=PaperQuery
        )

    def buildSRUQueriesForCodes(self, codes):
        sruQueries = []
        for i in range(0, len(codes), 10):
            codesForQuery = codes[i:i + 10]
            sruQuery = PaperQuery(
                startIndex=0,
                numRecords=10,
                codes=codesForQuery
            )
            sruQueries.append(sruQuery)
        return sruQueries

    def buildSRUQueriesForAllRecords(self):
        sruQuery = PaperQuery(
            startIndex=0,
            numRecords=1
        )
        numResults = self.indexer.getNumResultsForEachQuery([sruQuery])
        return self.indexer.makeIndexedQueries(numResults)

    def buildArkQueriesForCodes(self, codes):
        return [
            ArkQueryForNewspaperYears(code)
            for code in codes
        ]

