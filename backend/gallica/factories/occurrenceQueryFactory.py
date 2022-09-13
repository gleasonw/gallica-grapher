from cqlFactory import CQLFactory
from fetch import Fetch
from requestFactory import buildParser
from query import Query


class OccurrenceQueryFactory:

    def __init__(self):
        self.cql = CQLFactory()
        self.fetcher = Fetch('https://gallica.bnf.fr/SRU')
        self.parser = buildParser()

    def buildQueriesForOptions(self, options):
        cql = self.cql.buildStringsForOptions(options)
        numResultsForEachCQLstring = self.getNumResultsForCQL(cql)
        queries = self.indexQueries(numResultsForEachCQLstring)
        return queries

    def getNumResultsForCQL(self, cql):
        numResultsQueries = self.generateNumResultsQueries(cql)
        responses = self.fetcher.fetchAll(numResultsQueries)
        for query in responses:
            numResults = self.parser.numRecords(query.responseXML)
            url = query.url
            yield url, numResults

    def generateNumResultsQueries(self, cql):
        for cqlString in cql:
            yield Query(
                url=cqlString,
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def indexQueries(self, resultsForCQL):
        for cqlString, numResults in resultsForCQL:
            yield from self.makeQueriesWithIndices(cqlString, numResults)

    def makeQueriesWithIndices(self, cqlString, numResults):
        for i in range(1, numResults, 50):
            yield Query(
                url=cqlString,
                startIndex=i,
                numRecords=50,
                collapsing=False
            )

    def getTotalResults(self):
        return sum(numResults for url, numResults in self.fulfiller.numResultsForUrls)
