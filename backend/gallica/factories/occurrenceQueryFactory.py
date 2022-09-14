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

    def buildQueriesForTicketAndAddNumResults(self, ticket):
        cql = self.cql.buildStringsForTicket(ticket)
        queries = self.indexer.buildIndexQueries(cql)
        ticket.setQueries(queries)
        ticket.setEstimateNumResults(self.indexer.totalResults)
