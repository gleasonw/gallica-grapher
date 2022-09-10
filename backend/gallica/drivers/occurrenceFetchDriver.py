CHUNK_SIZE = 200


class OccurrenceFetchDriver:

    def __init__(
            self,
            options,
            parse,
            getURLsForOptions,
            makeQuery,
            insertRecords,
            fetchNoTrack,
            fetchAndTrack,
            progressTracker
    ):
        self.options = options
        self.parse = parse
        self.getUrlsForOptions = getURLsForOptions
        self.makeQuery = makeQuery
        self.fetchNoTrack = fetchNoTrack
        self.fetchAndTrack = fetchAndTrack
        self.insertRecords = insertRecords
        self.progressTracker = progressTracker

    def parse(self, xml):
        return self.parse.occurrences(xml)

    def insert(self, records):
        self.insertRecords(records)

    def prepareRecordsForInsert(self, records):
        return self.removeDuplicateRecords(records)

    def fetch(self, queries):
        return self.fetchAndTrack(queries, self.progressTracker)

    def getNumResultsForURLs(self, urls):
        numResultsQueries = self.generateNumResultsQueries(urls)
        responses = self.fetchNoTrack(numResultsQueries)
        for response in responses:
            numResults = self.parse.numRecords(response["recordXML"])
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

    def removeDuplicateRecords(self, records):
        seen = set()
        for record in records:
            if record.uniquenessCheck not in seen:
                seen.add(record.uniquenessCheck)
                yield record

