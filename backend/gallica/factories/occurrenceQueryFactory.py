from cqlFactory import CQLFactory
from parseFactory import buildParser
from queryIndexer import QueryIndexer
from batchedQueries import BatchedQueries


class OccurrenceQueryFactory:

    def __init__(self):
        self.cql = CQLFactory()
        self.parser = buildParser()
        self.indexer = QueryIndexer()
        self.queryBatcher = BatchedQueries(batchSize=200).batchQueries

    def buildQueriesForOptions(self, options):
        cql = self.cql.buildStringsForOptions(options)
        queries = self.indexer.buildIndexQueries(cql)
        return {
            'queries': self.queryBatcher(queries),
            'estimateNumResults': self.indexer.totalResults
        }
