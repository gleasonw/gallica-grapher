CHUNK_SIZE = 200


#TODO: move holdingresult logic into this class, search for missing records beforehand
class Fulfillment:

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
        self.SRUfetch = fetcher
        self.insertRecords = insertRecords
        self.progressTracker = None

    def setProgressTracker(self, progressTracker):
        self.progressTracker = progressTracker

    def search(self):
        chunkedQueries = self.buildQueries()
        for chunk in chunkedQueries:
            queriesWithResponseXML = self.fulfiller.fetcher(chunk)
            records = yield from (
                self.fulfiller.parse(query.responseXML) for query in queriesWithResponseXML
            )
            records = self.fulfiller.prepareRecordsForInsert(records)
            self.fulfiller.insert(records)

    def parse(self, xml):
        return self.parse.occurrences(xml)

    def insert(self, records):
        self.insertRecords(records)

    def prepareRecordsForInsert(self, records):
        return self.removeDuplicateRecords(records)

    def fetch(self, queries):
        return self.SRUfetch.fetchAndTrack(
            queries,
            self.progressTrackWithPaper
        )

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
            urls,
            makeQuery,
            paperFetcher,
            yearFetcher,
            insertPapers
    ):
        self.parse = parse
        self.makeQuery = makeQuery
        self.SRUfetch = paperFetcher
        self.ARKfetch = yearFetcher
        self.insertPapers = insertPapers

    def parse(self, xml):
        return self.parse.papers(xml)

    def fetch(self, queries):
        return self.fetcher.fetchNoTrack(queries)

    def prepareRecordsForInsert(self, records):
        recordCodes = [record for record in records]
        publishingRangeQueries = self.generateRangeQueries(recordCodes)
        yearQueriesWithResponse = self.ARKfetch.fetchNoTrack(publishingRangeQueries)
        recordsWithPublishingYears = self.addPublishingYearsToPaperRecord(
            records,
            yearQueriesWithResponse
        )
        return recordsWithPublishingYears

    def insert(self, records):
        self.insertPapers(records)

    def generateRangeQueries(self, codes):
        for code in codes:
            yield self.makeQuery(
                url=f'ark:/12148/{code}/date',
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def addPublishingYearsToPaperRecord(self, records, yearQueriesWithResponse):
        yearData = {}
        for query in yearQueriesWithResponse:
            code = query.url.split('/')[-2]
            yearData[code] = self.parse.yearsPublished(query.responseXML)
        for record in records:
            record.publishingYears = yearData[record.code]
            yield record





