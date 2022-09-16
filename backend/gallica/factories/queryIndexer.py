from fetch import Fetch
from parseFactory import buildParser
from query import Query


class QueryIndexer:

    def __init__(self, baseQueries, collapsing=False):
        self.fetch = Fetch('https://gallica.bnf.fr/SRU')
        self.parse = buildParser()
        self.makeQuery = Query
        self.collapsing = collapsing
        self.baseQueries = baseQueries

    def fetchNumResultsForQueries(self):
        self.baseQueries = list(self.fetch.fetchAll(self.baseQueries))
        totalResults = 0
        for query in self.baseQueries:
            numRecordsForBaseCQL = self.parse.numRecords(query.responseXML)
            totalResults += numRecordsForBaseCQL
            query.estimateNumRecordsToFetch = numRecordsForBaseCQL
        return totalResults

    def makeIndexedQueries(self):
        queries = []
        for query in self.baseQueries:
            for index in range(1, query.estimateNumRecordsToFetch, 50):
                queries.append(
                    Query(
                        cql=query.cql,
                        startIndex=index,
                        numRecords=50,
                        collapsing=False,
                        term=query.term
                    )
                )
        return queries
