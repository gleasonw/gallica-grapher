CHUNK_SIZE = 200


class Search:

    def __init__(self):
        pass

    def getEstimateSearchSize(self, search):
        return search.getTotalResults()

    def getRecordsForOptions(self, search):
        if isinstance(search, OccurrenceSearchFulfillment):
            numResultsForUrls = search.numResultsForUrls
        elif isinstance(search, PaperSearchFulfillment):
            numResultsForUrls = [
                (search.allPaperURL, search.numPapers)
            ]
        else:
            raise TypeError(f'Invalid fetch driver type: {type(search)}')
        self.fetchAndInsert(numResultsForUrls, search)

    def fetchAndInsert(self, numResultsForUrls, driver):
        chunkedQueries = self.buildQueries(numResultsForUrls, driver)
        for chunk in chunkedQueries:
            queriesWithResponseXML = driver.get(chunk)
            records = yield from (
                driver.parse(query.responseXML) for query in queriesWithResponseXML
            )
            records = driver.prepareRecordsForInsert(records)
            driver.insert(records)

    def buildQueries(self, numResultsForUrls, driver):
        indexedQueries = self.generateIndexedQueries(numResultsForUrls, driver)
        chunkedQueries = self.splitIntoCHUNK_SIZEchunks(indexedQueries)
        return chunkedQueries

    def generateIndexedQueries(self, numResultsForUrls, driver):
        for url, numResults in numResultsForUrls:
            yield self.makeQueriesWithIndices(url, numResults, driver)

    def makeQueriesWithIndices(self, url, numResults, driver):
        for i in range(1, numResults, 50):
            yield driver.makeQuery(
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


class OccurrenceSearchFulfillment:

    def __init__(
            self,
            parse,
            urls,
            makeQuery,
            insertRecords,
            fetcher
    ):
        self.parse = parse
        self.urls = urls
        self.makeQuery = makeQuery
        self.fetcher = fetcher
        self.insertRecords = insertRecords
        self.progressTracker = None
        self.numResultsForUrls = self.getNumResultsForURLs()

    def setProgressTracker(self, progressTracker):
        self.progressTracker = progressTracker

    def getTotalResults(self):
        return sum(numResults for url, numResults in self.numResultsForUrls)

    def getNumResultsForURLs(self):
        numResultsQueries = self.generateNumResultsQueries()
        responses = self.fetcher.fetchNoTrack(numResultsQueries)
        for response in responses:
            numResults = self.parse.numRecords(response["recordXML"])
            url = response["url"]
            yield url, numResults

    def generateNumResultsQueries(self):
        for url in self.urls:
            yield self.makeQuery(
                url=url,
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def parse(self, xml):
        return self.parse.occurrences(xml)

    def insert(self, records):
        self.insertRecords(records)

    def prepareRecordsForInsert(self, records):
        return self.removeDuplicateRecords(records)

    def fetch(self, queries):
        return self.fetcher.fetchAndTrack(
            queries,
            self.progressTrackWithPaper
        )


    def removeDuplicateRecords(self, records):
        seen = set()
        for record in records:
            if record.uniquenessCheck not in seen:
                seen.add(record.uniquenessCheck)
                yield record

    def progressTrackWithPaper(self, query, numWorkers):
        paper = self.parse.onePaperTitleFromOccurrenceBatch(
            query.responseXML
        )
        self.progressTracker(
            query,
            numWorkers,
            paper
        )


class PaperSearchFulfillment:

    def __init__(
            self,
            parse,
            getCQLstringsFor,
            makeQuery,
            fetcher,
            insertPapers
    ):
        self.parse = parse
        self.getCQLstringsFor = getCQLstringsFor
        self.makeQuery = makeQuery
        self.fetcher = fetcher
        self.insertPapers = insertPapers
        self.allPaperURL = 'dc.type all "fascicule" and ocrquality > "050.00"'
        self.numPapers = 0

    def parse(self, xml):
        return self.parse.papers(xml)

    def getTotalResults(self):
        allPaperQuery = self.getAllPaperQuery()
        queryWithResponse = self.fetcher.fetchNoTrack([allPaperQuery])
        responseXML = queryWithResponse[0].responseXML
        self.numPapers = self.parse.numRecords(responseXML)
        return self.numPapers

    def insert(self, records):
        self.insertPapers(records)

    def prepareRecordsForInsert(self, records):
        return self.addPublishingYearsToPaperRecord(records)

    def fetch(self, queries):
        return self.fetcher.fetchNoTrack(queries)

    def fetchRecordsFromCodes(self, paperCodes):
        batchedURLs = self.getCQLstringsFor(paperCodes)
        recordDataQueries = self.generateSelectCodeQueries(batchedURLs)
        publishingRangeQueries = self.generateRangeQueries(paperCodes)
        queriesWithResponse = self.fetcher.fetchNoTrack(recordDataQueries)
        yearQueriesWithResponse = self.fetcher.fetchNoTrack(publishingRangeQueries)
        records = self.getRecordsFromResponses(queriesWithResponse)
        recordsWithPublishingYears = self.addPublishingYearsToPaperRecord(
            records,
            yearQueriesWithResponse
        )
        self.insertPapers(recordsWithPublishingYears)

    def generateSelectCodeQueries(self, batchedURLs):
        for url in batchedURLs:
            yield self.makeQuery(
                url=url,
                startIndex=1,
                numRecords=50,
                collapsing=True
            )

    def generateRangeQueries(self, codes):
        for code in codes:
            yield self.makeQuery(
                url=f'ark:/12148/{code}/date',
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def getRecordsFromResponses(self, queriesWithResponse):
        xml = yield from (query.responseXML for query in queriesWithResponse)
        records = self.parse.records(xml)
        return records

    def addPublishingYearsToPaperRecord(self, records, yearQueriesWithResponse):
        yearData = {}
        for query in yearQueriesWithResponse:
            code = query.url.split('/')[-2]
            yearData[code] = self.parse.yearsPublished(query.responseXML)
        for record in records:
            record.publishingYears = yearData[record.code]
            yield record

    def getAllPaperQuery(self):
        return self.makeQuery(
            url='dc.type all "fascicule" and ocrquality > "050.00"',
            startIndex=1,
            numRecords=1,
            collapsing=False
        )





