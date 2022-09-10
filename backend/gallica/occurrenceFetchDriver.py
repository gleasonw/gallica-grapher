CHUNK_SIZE = 200


class OccurrenceFetchDriver:

    def __init__(
            self,
            options,
            parse,
            getUrlsForSettings,
            makeQuery,
            insertRecords,
            fetchNoTrack,
            fetchAndTrack,
            progressTracker
    ):
        self.options = options
        self.parseToRecords = parse
        self.getUrlsForOptions = getUrlsForSettings
        self.makeQuery = makeQuery
        self.fetchNoTrack = fetchNoTrack
        self.fetchAndTrack = fetchAndTrack
        self.insertRecords = insertRecords
        self.progressTracker = progressTracker

    def runFetchAndInsertRecords(self):
        urls = self.getUrlsForOptions(self.options)
        numResultsForUrls = self.getNumResultsForURLs(urls)
        indexedQueries = self.generateIndexedQueries(numResultsForUrls)
        chunkedQueries = self.splitIntoCHUNK_SIZEchunks(indexedQueries)
        for chunk in chunkedQueries:
            xml = self.fetchAndTrack(chunk, self.progressTracker)
            records = self.parseToRecords(self, xml)
            records = self.removeDuplicateRecords(records)
            self.insertRecords(records)

    def getNumResultsForURLs(self, urls):
        numResultsQueries = self.generateNumResultsQueries(urls)
        responses = self.fetchNoTrack(numResultsQueries)
        for response in responses:
            numResults = self.parseToRecords.numRecords(response["recordXML"])
            url = response["url"]
            yield url, numResults

    def generateNumResultsQueries(self, urls):
        for url in urls:
            yield self.makeQuery(
                url=url,
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def generateIndexedQueries(self, numResultsForUrls):
        for url, numResults in numResultsForUrls:
            yield self.buildIndex(url, numResults)

    def buildIndex(self, url, numResults):
        for i in range(1, numResults, 50):
            yield self.makeQuery(
                url=url,
                startIndex=i,
                numRecords=50,
                collapsing=False
            )

    def splitIntoCHUNK_SIZEchunks(self, indexedQueries):
        allChunks = []
        chunk = []
        for query in indexedQueries:
            if len(chunk) < CHUNK_SIZE:
                chunk.append(query)
            else:
                allChunks.append(chunk)
                chunk = [query]
        return allChunks

    def removeDuplicateRecords(self, records):
        seen = set()
        for record in records:
            if record.uniquenessCheck not in seen:
                seen.add(record.uniquenessCheck)
                yield record

