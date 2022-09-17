from gallica.fetch import Fetch
from gallica.factories.parseFactory import buildParser
from gallica.query import Query
from gallica.query import PaperQuery


class QueryIndexer:

    def __init__(self, baseQueries):
        self.fetch = Fetch('https://gallica.bnf.fr/SRU')
        self.parse = buildParser()
        self.makeQuery = Query
        self.baseQueries = baseQueries

    def fetchNumResultsForQueries(self):
        responses = self.fetch.fetchAll(self.baseQueries)
        totalResults = 0
        for data in responses:
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

    def makeIndexedPaperQueries(self):
        queries = []
        for query in self.baseQueries:
            for index in range(1, query.estimateNumRecordsToFetch, 50):
                queries.append(
                    PaperQuery(
                        cql=query.cql,
                        startIndex=index
                    )
                )
        return queries
