from fetch import Fetch
from parseFactory import buildParser
from query import Query


class QueryIndexer:

    def __init__(self):
        self.fetch = Fetch('https://gallica.bnf.fr/SRU')
        self.parse = buildParser()
        self.totalResults = 0
        self.makeQuery = Query

    def buildIndexQueries(self, cql):
        indexedQueryGeneratorsForCQL = (
            self.makeQueriesWithIndices(cqlString)
            for cqlString in cql
        )
        return indexedQueryGeneratorsForCQL

    def makeQueriesWithIndices(self, cqlString):
        numResults = self.getNumResults(cqlString)
        self.totalResults += numResults
        for i in range(1, numResults, 50):
            yield self.makeQuery(
                url=cqlString,
                startIndex=i,
                numRecords=50,
                collapsing=False
            )

    def getNumResults(self, cqlString):
        numResultsQuery = self.makeQuery(
            url=cqlString,
            startIndex=1,
            numRecords=1,
            collapsing=False
        )
        response = self.fetch.fetchAll([numResultsQuery])
        responseXML = response.responseXML
        return self.parse.numRecords(responseXML)

