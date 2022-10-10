from lxml import etree
from gallica.dto.arkRecord import ArkRecord
from gallica.factories.paperQueryFactory import PaperQueryFactory
from gallica.recordGetter import RecordGetter
from fetchComponents.concurrentfetch import ConcurrentFetch
from paperRecord import PaperRecord
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
            parseData=parse
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
            yield from self.generateArkRecord(response.xml, response.query)

    def generateArkRecord(self, xml, query):
        years = self.parser.getYears(xml)
        code = query.getCode()
        yield ArkRecord(
            code=code,
            years=years
        )
