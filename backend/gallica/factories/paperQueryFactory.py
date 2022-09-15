from cqlStringForPaperCodes import CQLStringForPaperCodes
from queryIndexer import QueryIndexer
from batchedQueries import BatchedQueries
from query import Query


class PaperQueryFactory:

    def __init__(self):
        self.cql = CQLStringForPaperCodes()
        self.indexer = QueryIndexer(collapsing=True)
        self.queryBatcher = BatchedQueries(batchSize=200).batchQueries

    def buildSRUQueriesForCodes(self, codes):
        cqlStrings = self.cql.build(codes)
        indexedQueries = self.indexer.makeQueriesIndexedOnNumResultsForBaseCQL(cqlStrings)
        return indexedQueries

    def buildARKQueriesForCodes(self, codes):
        queries = [
            Query(
                cql=f'/{code}/date',
                startIndex=1,
                numRecords=1,
                collapsing=False
            )
            for code in codes
        ]
        return self.queryBatcher(queries)

    def buildAllRecordsQueries(self) -> list[list[Query]]:
        queries = self.indexer.makeQueriesIndexedOnNumResultsForBaseCQL(
            ['dc.type all "fascicule" and ocrquality > "050.00"']
        )
        return self.queryBatcher(queries)




