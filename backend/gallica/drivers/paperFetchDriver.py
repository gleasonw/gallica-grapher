class PaperFetchDriver:

    def __init__(
            self,
            parse,
            getCQLstringsFor,
            makeQuery,
            fetchNoTrack,
            insertPapers
    ):
        self.parse = parse
        self.getCQLstringsFor = getCQLstringsFor
        self.makeQuery = makeQuery
        self.fetchNoTrack = fetchNoTrack
        self.insertPapers = insertPapers
        self.allPaperURL = 'dc.type all "fascicule" and ocrquality > "050.00"'

    def parse(self, xml):
        return self.parse.papers(xml)

    def insert(self, records):
        self.insertPapers(records)

    def prepareRecordsForInsert(self, records):
        return self.addPublishingYearsToPaperRecord(records)

    def fetch(self, queries):
        return self.fetchNoTrack(queries)

    def fetchRecordsFromCodes(self, paperCodes):
        batchedURLs = self.getCQLstringsFor(paperCodes)
        recordDataQueries = self.generateSelectCodeQueries(batchedURLs)
        publishingRangeQueries = self.generateRangeQueries(paperCodes)
        queriesWithResponse = self.fetchNoTrack(recordDataQueries)
        yearQueriesWithResponse = self.fetchNoTrack(publishingRangeQueries)
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