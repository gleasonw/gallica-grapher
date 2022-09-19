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
        response = self.SRUfetch.fetchAll(queries)
        for data, cql in response:
            records = self.parse.papers(data)
            recordsWithPublishingYears = self.getPublishingYearsForRecords(records)
            self.insertIntoPapers(recordsWithPublishingYears)

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
        for data, code in yearQueriesWithResponse:
            try:
                yearData[code] = self.parse.yearsPublished(data)
            except LxmlError:
                print("bad years for code: ", code)
        for record in records:
            record.publishingYears = yearData.get(record.code, [])
            yield record
