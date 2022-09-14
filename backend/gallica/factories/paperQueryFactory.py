from cqlFactory import CQLStringForPaperCodes
from queryIndexer import QueryIndexer
from query import Query
from batchedQueries import BatchedQueries


class PaperQueryFactory:

    def __init__(self):
        self.cql = CQLStringForPaperCodes()
        self.indexer = QueryIndexer()
        self.queryBatcher = BatchedQueries(batchSize=200).batchQueries

    def buildSRUQueriesForCodes(self, codes) -> list[list[Query]]:
        cqlStrings = self.cql.build(codes)
        queries = self.indexer.buildIndexQueries(cqlStrings)
        return self.queryBatcher(queries)

    def buildARKQueriesForCodes(self, codes) -> list[list[Query]]:
        queries = [
            Query(
                url=f'/{code}/date',
                startIndex=1,
                numRecords=1,
                collapsing=False
            )
            for code in codes
        ]
        return self.queryBatcher(queries)

    def buildAllRecordsQueries(self) -> list[list[Query]]:
        cqlString = 'dc.type all "fascicule" and ocrquality > "050.00"'
        queries = self.indexer.buildIndexQueries([cqlString])
        return self.queryBatcher(queries)




