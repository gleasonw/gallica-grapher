from lxml.etree import LxmlError


class PaperSearchRunner:

    def __init__(
            self,
            parse,
            sruFetch,
            paperQueryFactory,
            arkFetch,
            addPapersToDB=None
    ):
        self.parse = parse
        self.queryFactory = paperQueryFactory
        self.SRUfetch = sruFetch
        self.ARKfetch = arkFetch
        self.addPapersToDB = addPapersToDB

    def addRecordDataForTheseCodesToDB(self, codes):
        print(f'Adding {len(codes)} paper records to DB')
        queries = list(self.queryFactory.buildSRUQueriesForCodes(codes))
        return self.doSearch(queries)

    def addAllFetchableRecordsToDB(self):
        queries = self.queryFactory.buildAllRecordsQueries()
        records = self.doSearch(queries)
        self.addPapersToDB(records)

    def doSearch(self, queries):
        response = self.SRUfetch.fetchAll(queries)
        for data, cql in response:
            records = self.parse.papers(data)
            yield from self.getPublishingYearsForRecords(records)

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
