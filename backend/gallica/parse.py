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
        self.paperDriverClass = paperDriver
        self.occurrenceDriverClass = occurrenceDriver
        self.makePaperRecord = makePaperRecord
        self.makeOccurrenceRecord = makeOccurrenceRecord
        self.xmlParser = xmlParser

    def records(self, fetchDriver, xml) -> list:
        xmlRoot = etree.fromstring(xml)
        recordRoots = xmlRoot.findall(
            "{http://www.loc.gov/zing/srw/}record")
        recordData = [root[2][0] for root in recordRoots]
        if isinstance(fetchDriver, self.paperDriverClass):
            return self.papers(recordData)
        elif isinstance(fetchDriver, self.occurrenceDriverClass):
            return self.occurrences(recordData)
        else:
            raise Exception("Unknown fetch driver type")

    def papers(self, records) -> list:
        for record in records:
            self.xmlParser.setXML(record)
            newRecord = self.makePaperRecord(
                code=self.xmlParser.getPaperCode(),
                title=self.xmlParser.getPaperTitle(),
                url=self.xmlParser.getURL(),
            )
            yield newRecord

    def occurrences(self, records) -> list:
        for record in records:
            self.xmlParser.setXML(record)
            newRecord = self.makeOccurrenceRecord(
                paperCode=self.xmlParser.getPaperCode(),
                date=self.xmlParser.getDate(),
                url=self.xmlParser.getURL()
            )
            yield newRecord

    def numRecords(self, xml) -> int:
        xmlRoot = etree.fromstring(xml)
        self.xmlParser.setXML(xmlRoot)
        return self.xmlParser.getNumRecords()

    def yearsPublished(self, xml) -> list:
        xmlRoot = etree.fromstring(xml)
        self.xmlParser.setXML(xmlRoot)
        return self.xmlParser.getYearsPublished()

    def onePaperTitleFromOccurrenceBatch(self, xml) -> str:
        xmlRoot = etree.fromstring(xml)
        self.xmlParser.setXML(xmlRoot)
        return self.xmlParser.getPaperTitle()

