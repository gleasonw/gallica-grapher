from fetch import Fetch
from parseFactory import buildParser
from query import Query


class QueryIndexer:

    def __init__(self, collapsing=False):
        self.fetch = Fetch('https://gallica.bnf.fr/SRU')
        self.parse = buildParser()
        self.totalResultsForTicket = 0
        self.makeQuery = Query
        self.collapsing = collapsing

    def makeQueriesIndexedOnNumResultsForBaseCQL(self, cql):
        baseQueries = self.buildBaseQueriesFromCQL(cql)
        responseXMLForBaseQueries = self.fetch.fetchAll(baseQueries)
        for response in responseXMLForBaseQueries:
            numRecordsForBase = self.parse.numRecords(response)
            self.totalResultsForTicket += numRecordsForBase
            for index in range(1, numRecordsForBase, 50):
                yield Query(
                    cql=response.cql,
                    startIndex=index,
                    numRecords=50,
                    collapsing=False,
                    term=response.term
                )

    def buildBaseQueriesFromCQL(self, cql):
        for cqlString in cql:
            yield self.makeQuery(
                cql=cqlString,
                startIndex=1,
                numRecords=1,
                collapsing=self.collapsing
            )
