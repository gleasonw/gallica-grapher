from lxml.etree import LxmlError


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
        queries = list(self.queryFactory.buildSRUQueriesForCodes(codes))
        self.doSearch(queries)

    def addAllFetchableRecordsToDB(self):
        queries = self.queryFactory.buildAllRecordsQueries()
        self.doSearch(queries)

    def doSearch(self, queries):
        queriesWithResponseData = self.SRUfetch.fetchAll(queries)
        records = self.convertQueriesToRecords(queriesWithResponseData)
        recordsWithPublishingYears = self.getPublishingYearsForRecords(records)
        self.insertIntoPapers(recordsWithPublishingYears)

    def convertQueriesToRecords(self, queries):
        for query in queries:
            records = self.parse.papers(query.responseXML)
            yield from records

    def getPublishingYearsForRecords(self, records):
        records = list(records)
        codes = (record.code for record in records)
        publishingRangeQueries = self.queryFactory.buildARKQueriesForCodes(codes)
        yearQueriesWithResponse = self.ARKfetch.fetchAll(publishingRangeQueries)
        recordsWithPublishingYears = self.addPublishingYearsToPaperRecord(
            records,
            yearQueriesWithResponse
        )
        yield from recordsWithPublishingYears

    def addPublishingYearsToPaperRecord(self, records, yearQueriesWithResponse):
        yearData = {}
        for query in yearQueriesWithResponse:
            try:
                code = query.code
                yearData[code] = self.parse.yearsPublished(query.responseXML)
            except LxmlError:
                print("bad years for code: ", query.code)
        for record in records:
            record.publishingYears = yearData.get(record.code, [])
            yield record
