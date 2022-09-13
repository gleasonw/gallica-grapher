from cqlFactory import CQLStringForPaperCodes
from queryIndexer import QueryIndexer
from query import Query
from batchedQueries import BatchedQueries


class PaperQueryFactory:

    def __init__(self):
        self.cql = CQLStringForPaperCodes()
        self.indexer = QueryIndexer()
        self.queryBatcher = BatchedQueries(batchSize=200).batchQueries

    def buildSRUQueriesForCodes(self, codes):
        cqlStrings = self.cql.build(codes)
        queries = self.indexer.buildIndexQueries(cqlStrings)
        return self.queryBatcher(queries)

    def buildARKQueriesForCodes(self, codes):
        for code in codes:
            yield Query(
                url=f'/{code}/date',
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def getAllRecordsQueries(self):
        cqlString = 'dc.type all "fascicule" and ocrquality > "050.00"'
        return self.indexer.buildIndexQueries([cqlString])




