class PaperSearch:

    def __init__(
            self,
            SRURecordGetter,
            ARKRecordGetter,
            queryMaker,
            insertIntoPapers=None
    ):
        self.queryMaker = queryMaker
        self.SRURecordGetter = SRURecordGetter
        self.ARKRecordGetter = ARKRecordGetter
        self.insertIntoPapers = insertIntoPapers

    def getRecordsForTheseCodes(self, codes):
        sruQueries = self.queryMaker.buildSRUQueriesForCodes(codes)
        arkQueries = self.queryMaker.buildArkQueriesForCodes(codes)
        sruRecords = self.SRURecordGetter.getFromQueries(sruQueries)
        arkRecords = self.ARKRecordGetter.getFromQueries(arkQueries)
        return self.composeRecords(sruRecords, arkRecords)

    def putAllPaperRecordsIntoDB(self):
        sruQueries = self.queryMaker.buildSRUQueriesForAllRecords()
        sruRecords = list(self.SRURecordGetter.getFromQueries(sruQueries))
        arkQueries = self.queryMaker.buildArkQueriesForCodes(
            codes=[record.code for record in sruRecords]
        )
        arkRecords = self.ARKRecordGetter.getFromQueries(arkQueries)
        paperRecordsWithYears = self.composeRecords(sruRecords, arkRecords)
        return self.insertIntoPapers(paperRecordsWithYears)

    def composeRecords(self, sruRecords, arkRecords):
        yearsFromCode = {
            ark.code: ark.years
            for ark in arkRecords
        }
        for record in sruRecords:
            record.addYearsFromArk(
                yearsFromCode.get(record.code, [])
            )
            yield record


