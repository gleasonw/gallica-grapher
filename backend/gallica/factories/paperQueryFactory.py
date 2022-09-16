from gallica.factories.cqlStringForPaperCodes import CQLStringForPaperCodes
from gallica.factories.queryIndexer import QueryIndexer
from gallica.query import Query
from gallica.query import ArkQuery
from gallica.query import PaperQuery
from gallica.query import NumPapersOnGallicaQuery


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
        queries = [ArkQuery(code) for code in codes]
        return queries

    def buildAllRecordsQueries(self) -> list[list[Query]]:
        query = self.makeNumPapersQuery(
            'dc.type all "fascicule" and ocrquality > "050.00"'
        )
        indexer = self.makeIndexer([query])
        numResults = indexer.fetchNumResultsForQueries()
        print(numResults)
        queries = indexer.makeIndexedPaperQueries()
        return queries
