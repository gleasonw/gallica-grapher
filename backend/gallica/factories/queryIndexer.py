from fetch import Fetch
from requestFactory import buildParser
from query import Query


class QueryIndexer:

    def __init__(self):
        self.fetch = Fetch('https://gallica.bnf.fr/SRU')
        self.parse = buildParser()
        self.totalResults = 0

    def buildIndexQueries(self, cql):
        for cqlString in cql:
            yield from self.makeQueriesWithIndices(cqlString)

    def makeQueriesWithIndices(self, query):
        numResults = self.getNumResults(query)
        self.totalResults += numResults
        for i in range(1, numResults, 50):
            yield Query(
                url=query.url,
                startIndex=i,
                numRecords=50,
                collapsing=False
            )

    def getNumResults(self, cqlString):
        numResultsQuery = Query(
            url=cqlString.url,
            startIndex=1,
            numRecords=1,
            collapsing=False
        )
        response = self.fetch.fetchAll([numResultsQuery])
        responseXML = response.responseXML
        return self.parse.numRecords(responseXML)

