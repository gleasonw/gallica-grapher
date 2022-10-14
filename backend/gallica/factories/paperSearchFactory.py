from gallica.dto.arkRecord import ArkRecord
from gallica.factories.paperQueryFactory import PaperQueryFactory
from gallica.recordGetter import RecordGetter
from gallica.fetchComponents.concurrentFetch import ConcurrentFetch
from gallica.dto.paperRecord import PaperRecord
from gallica.paperSearch import PaperSearch


class PaperSearchFactory:

    def __init__(
            self,
            parse,
            SRUapi,
            insertIntoPapers=None
    ):
        self.parse = parse
        self.SRUapi = SRUapi
        self.insertIntoPapers = insertIntoPapers
        self.queryMaker = PaperQueryFactory(
            gallicaAPI=SRUapi,
            parse=parse
        )
        self.parsePaperRecords = ParsePaperRecords(parse)
        self.SRURecordGetter = RecordGetter(
            gallicaAPI=SRUapi,
            parseData=ParsePaperRecords(parse)
        )
        self.ARKRecordGetter = RecordGetter(
            gallicaAPI=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
            parseData=ParseArkRecord(parse)
        )
        self.insertIntoPapers = insertIntoPapers

    def buildSearch(self):
        return PaperSearch(
            SRURecordGetter=self.SRURecordGetter,
            ARKRecordGetter=self.ARKRecordGetter,
            queryMaker=self.queryMaker,
            insertIntoPapers=self.insertIntoPapers
        )


class ParsePaperRecords:

    def __init__(self, parser):
        self.parser = parser

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generatePaperRecords(response.xml)

    def generatePaperRecords(self, xml):
        for record in self.parser.getRecordsFromXML(xml):
            yield PaperRecord(
                code=self.parser.getPaperCodeFromRecord(record),
                title=self.parser.getPaperTitleFromRecord(record),
                url=self.parser.getURLfromRecord(record),
            )


class ParseArkRecord:

    def __init__(self, parser):
        self.parser = parser

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generateArkRecord(response.xml, response.query)

    def generateArkRecord(self, xml, query):
        years = self.parser.getYearsPublished(xml)
        code = query.getCode()
        yield ArkRecord(
            code=code,
            years=years
        )
