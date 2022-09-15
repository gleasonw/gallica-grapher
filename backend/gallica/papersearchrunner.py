class PaperSearchRunner:

    def __init__(
            self,
            parse,
            sruFetch,
            paperQueryFactory,
            arkFetch,
            insert
    ):
        self.parse = parse
        self.queryFactory = paperQueryFactory
        self.SRUfetch = sruFetch
        self.ARKfetch = arkFetch
        self.insertIntoPapers = insert

    def addRecordDataForTheseCodesToDB(self, codes):
        queries = self.queryFactory.buildSRUQueriesForCodes(codes)
        self.doSearch(queries)

    def addAllFetchableRecordsToDB(self):
        queries = self.queryFactory.buildSRUqueriesForAllRecords()
        self.doSearch(queries)

    def doSearch(self, queries):
        queriesWithResponseData = self.SRUfetch.fetchAll(queries)
        records = list(self.convertQueriesToRecords(queriesWithResponseData))
        recordsWithPublishingYears = self.getPublishingYearsForRecords(records)
        self.insertIntoPapers(recordsWithPublishingYears)

    def convertQueriesToRecords(self, queries):
        for query in queries:
            records = self.parse.papers(query.responseXML)
            yield from records

    def getPublishingYearsForRecords(self, records):
        recordCodes = (record.code for record in records)
        publishingRangeQueries = self.queryFactory.buildARKQueriesForCodes(recordCodes)
        yearQueriesWithResponse = self.ARKfetch.fetchAll(publishingRangeQueries)
        recordsWithPublishingYears = self.addPublishingYearsToPaperRecord(
            records,
            yearQueriesWithResponse
        )
        yield from recordsWithPublishingYears

    def addPublishingYearsToPaperRecord(self, records, yearQueriesWithResponse):
        yearData = {}
        for query in yearQueriesWithResponse:
            code = query.code
            yearData[code] = self.parse.yearsPublished(query.responseXML)
        for record in records:
            record.publishingYears = yearData[record.code]
            yield record
