from lxml import etree
from arkRecord import ArkRecord
from gallica.factories.paperQueryFactory import PaperQueryFactory
from gallica.recordGetter import RecordGetter
from fetchComponents.concurrentfetch import ConcurrentFetch
from paperRecord import PaperRecord


class PaperSearch:

    def __init__(
            self,
            parse,
            SRUapi,
            insertIntoPapers=None
    ):
        self.queryMaker = PaperQueryFactory(
            gallicaAPI=SRUapi,
            parse=parse
        )
        self.parsePaperRecords = ParsePaperRecords(parse)
        self.SRURecordGetter = RecordGetter(
            gallicaAPI=SRUapi,
            parseData=parse
        )
        self.ARKRecordGetter = RecordGetter(
            gallicaAPI=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
            parseData=ParseArkRecord(parse)
        )
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
            [record.code for record in sruRecords]
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


class ParsePaperRecords:

    def __init__(self, parser):
        self.parser = parser

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generatePaperRecords(response.xml)

    def generatePaperRecords(self, xml):
        elements = etree.fromstring(xml)
        if elements.find("{http://www.loc.gov/zing/srw/}records") is None:
            return []
        for recordXML in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.parser.getDataFromRecordRoot(recordXML)
            yield PaperRecord(
                code=self.parser.getPaperCode(data),
                title=self.parser.getPaperTitle(data),
                url=self.parser.getURL(data),
            )


class ParseArkRecord:

    def __init__(self, parser):
        self.parser = parser

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield self.generateArkRecord(response.xml, response.query)

    def generateArkRecord(self, xml, query):
        years = self.parser.getYears(xml)
        code = query.getCode()
        yield ArkRecord(
            code=code,
            years=years
        )
