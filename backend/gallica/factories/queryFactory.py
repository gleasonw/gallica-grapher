class QueryFactory:

    def __init__(self, options):
        self.options = options


    def buildQueries(self):
        indexedQueries = self.generateIndexedQueries()
        chunkedQueries = self.splitIntoCHUNK_SIZEchunks(indexedQueries)
        return chunkedQueries

    def generateIndexedQueries(self):
        for url, numResults in self.fulfiller.numResultsForUrls:
            yield self.makeQueriesWithIndices(url, numResults)

    def makeQueriesWithIndices(self, url, numResults):
        for i in range(1, numResults, 50):
            yield self.fulfiller.makeQuery(
                url=url,
                startIndex=i,
                numRecords=50,
                collapsing=False
            )

    def getNumResultsForURLs(self):
        numResultsQueries = self.generateNumResultsQueries()
        responses = self.fulfiller.fetch(numResultsQueries)
        for response in responses:
            numResults = self.fulfiller.parse.numRecords(response["recordXML"])
            url = response["url"]
            yield url, numResults

    def generateNumResultsQueries(self):
        for url in self.fulfiller.urls:
            yield self.fulfiller.makeQuery(
                url=url,
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def getTotalResults(self):
        return sum(numResults for url, numResults in self.fulfiller.numResultsForUrls)