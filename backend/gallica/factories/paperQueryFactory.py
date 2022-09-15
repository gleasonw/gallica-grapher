from cqlStringForPaperCodes import CQLStringForPaperCodes
from queryIndexer import QueryIndexer
from query import Query
from query import ArkQuery
from query import PaperQuery


class PaperQueryFactory:

    def __init__(self):
        self.cql = CQLStringForPaperCodes()
        self.makeIndexer = lambda cql: QueryIndexer(cql, collapsing=True)

    def buildSRUQueriesForCodes(self, codes):
        cqlStrings = self.cql.build(codes)
        for cql in cqlStrings:
            yield PaperQuery(cql)

    def buildARKQueriesForCodes(self, codes):
        queries = [ArkQuery(code) for code in codes]
        return queries

    def buildAllRecordsQueries(self) -> list[list[Query]]:
        indexer = self.makeIndexer(
            ['dc.type all "fascicule" and ocrquality > "050.00"']
        )
        queries = indexer.makeIndexedQueries()
        return queries




