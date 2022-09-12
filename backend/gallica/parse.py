from lxml import etree


class Parse:

    def __init__(
            self,
            makePaperRecord,
            makeOccurrenceRecord,
            xmlParser
    ):
        self.makePaperRecord = makePaperRecord
        self.makeOccurrenceRecord = makeOccurrenceRecord
        self.xmlParser = xmlParser

    def papers(self, records) -> list:
        elements = etree.fromstring(records)
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            self.xmlParser.setXML(record)
            newRecord = self.makePaperRecord(
                code=self.xmlParser.getPaperCode(),
                title=self.xmlParser.getPaperTitle(),
                url=self.xmlParser.getURL(),
            )
            yield newRecord

    def occurrences(self, records) -> list:
        elements = etree.fromstring(records)
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
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
        record = xmlRoot.find("{http://www.loc.gov/zing/srw/}record")
        self.xmlParser.setXML(record)
        return self.xmlParser.getPaperTitle()

