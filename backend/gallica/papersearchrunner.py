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
        queries = self.queryFactory.buildSRUqueriesForCodes(codes)
        self.doSearch(queries)

    def addAllFetchableRecordsToDB(self):
        queries = self.queryFactory.buildSRUqueriesForAllRecords()
        self.doSearch(queries)

    def doSearch(self, queries):
        for queryBatch in queries:
            queriesWithResponseData = self.SRUfetch.fetchNoTrack(queryBatch)
            recordsWithPublishingYears = self.getPublishingYearsForRecords(queriesWithResponseData)
            self.insertIntoPapers(recordsWithPublishingYears)

    def getPublishingYearsForRecords(self, records):
        recordCodes = (record.code for record in records)
        publishingRangeQueries = self.queryFactory.buildArkQueriesForCodes(recordCodes)
        yearQueriesWithResponse = self.ARKfetch.fetchNoTrack(publishingRangeQueries)
        recordsWithPublishingYears = self.addPublishingYearsToPaperRecord(
            records,
            yearQueriesWithResponse
        )
        return recordsWithPublishingYears

    def addPublishingYearsToPaperRecord(self, records, yearQueriesWithResponse):
        yearData = {}
        for query in yearQueriesWithResponse:
            code = query.cql.split('/')[-2]
            yearData[code] = self.parse.yearsPublished(query.responseXML)
        for record in records:
            record.publishingYears = yearData[record.code]
            yield record
