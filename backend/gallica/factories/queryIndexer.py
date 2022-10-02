from fetchComponents.concurrentfetch import ConcurrentFetch
from gallica.factories.parseFactory import buildParser
from fetchComponents.query import *


class QueryIndexer:

    def __init__(self, baseQueries):
        self.fetch = ConcurrentFetch('https://gallica.bnf.fr/SRU')
        self.parse = buildParser()
        self.makeQuery = Query
        self.baseQueries = {query.cql: query for query in baseQueries}

    def fetchNumResultsForQueries(self):
        responses = self.fetch.fetchAll(self.baseQueries.values())
        totalResults = 0
        for data, cql in responses:
            numRecordsForBaseCQL = self.parse.numRecords(data)
            totalResults += numRecordsForBaseCQL
            self.baseQueries[cql].estimateNumRecordsToFetch = numRecordsForBaseCQL
        return totalResults

    def makeIndexedQueries(self):
        for query in self.baseQueries.values():
            for index in range(1, query.estimateNumRecordsToFetch, 50):
                yield Query(
                    cql=query.cql,
                    startIndex=index,
                    numRecords=50,
                    collapsing=False,
                    term=query.term
                )

    def makeIndexedPaperQueries(self, totalResults):
        queries = []
        for cql in self.baseQueries:
            for index in range(1, totalResults, 50):
                queries.append(
                    PaperQuery(
                        cql=cql,
                        startIndex=index
                    )
                )
        return queries
