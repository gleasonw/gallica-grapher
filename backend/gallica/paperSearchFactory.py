from paperQueryFactory import PaperQueryFactory
from recordGetter import RecordGetter
from concurrentFetch import ConcurrentFetch
from gallica.paperSearch import PaperSearch
from parseArkRecord import ParseArkRecord
from parsePaperRecords import ParsePaperRecords


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


