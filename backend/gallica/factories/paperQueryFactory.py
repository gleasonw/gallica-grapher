from gallica.factories.cqlStringForPaperCodes import CQLStringForPaperCodes
from gallica.factories.allQueryIndexer import AllQueryIndexer
from fetchComponents.query import *


class PaperQueryFactory:

    def __init__(self):
        self.cql = CQLStringForPaperCodes()
        self.makeIndexer = lambda cql: AllQueryIndexer(cql)
        self.makeNumPapersQuery = lambda cql: NumPapersOnGallicaQuery(cql)

    def buildSRUQueriesForCodes(self, codes):
        cqlStrings = self.cql.build(codes)
        for cql in cqlStrings:
            yield PaperQuery(cql, startIndex=1)

    def buildARKQueriesForCodes(self, codes):
        queries = [ArkQueryForNewspaperYears(code) for code in codes]
        return queries

    def buildAllRecordsQueries(self) -> list:
        query = self.makeNumPapersQuery(
            'dc.type all "fascicule" and ocrquality > "050.00"'
        )
        indexer = self.makeIndexer([query])
        totalResults = indexer.fetchNumResultsForQueries()
        queries = indexer.makeIndexedPaperQueries(totalResults)
        return queries
