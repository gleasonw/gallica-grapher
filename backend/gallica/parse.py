from lxml import etree


class Parse:

    def __init__(
            self,
            paperDriver,
            occurrenceDriver,
            makePaperRecord,
            makeOccurrenceRecord,
            xmlParser
    ):
        self.paperDriver = paperDriver
        self.occurrenceDriver = occurrenceDriver
        self.makePaperRecord = makePaperRecord
        self.makeOccurrenceRecord = makeOccurrenceRecord
        self.xmlParser = xmlParser

    def parse(self, fetchDriver, xml) -> list:
        xmlRoot = etree.fromstring(xml)
        recordRoots = xmlRoot.findall(
            "{http://www.loc.gov/zing/srw/}record")
        recordData = [root[2][0] for root in recordRoots]
        if fetchDriver == self.paperDriver:
            return self.parsePapers(recordData)
        elif fetchDriver == self.occurrenceDriver:
            return self.parseOccurrence(recordData)
        else:
            raise Exception("Unknown fetch driver type")

    def parsePapers(self, records) -> list:
        for record in records:
            self.xmlParser.setXML(record)
            newRecord = self.makePaperRecord(
                code=self.xmlParser.getPaperCode(),
                title=self.xmlParser.getPaperTitle(),
                url=self.xmlParser.getURL(),
            )
            yield newRecord

    def parseOccurrence(self, records) -> list:
        for record in records:
            self.xmlParser.setXML(record)
            newRecord = self.makeOccurrenceRecord(
                paperCode=self.xmlParser.getPaperCode(),
                date=self.xmlParser.getDate(),
                url=self.xmlParser.getURL()
            )
            yield newRecord

