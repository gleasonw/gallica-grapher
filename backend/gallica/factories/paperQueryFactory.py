from gallica.factories.cqlStringForPaperCodes import CQLStringForPaperCodes
from gallica.factories.queryIndexer import QueryIndexer
from fetchComponents.query import *


class PaperQueryFactory:

    def __init__(self):
        self.cql = CQLStringForPaperCodes()
        self.makeIndexer = lambda cql: QueryIndexer(cql)
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
        indexer.fetchNumResultsForQueries()
        queries = indexer.makeIndexedPaperQueries()
        return queries
