from lxml import etree


class Parse:

    def __init__(
            self,
            makePaperRecord,
            makeOccurrenceRecord,
            recordParser
    ):
        self.makePaperRecord = makePaperRecord
        self.makeOccurrenceRecord = makeOccurrenceRecord
        self.makeRecordParser = lambda data: recordParser(data)

    def papers(self, responseXML) -> list:
        elements = etree.fromstring(responseXML)
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.getDataFromRecordRoot(record)
            recordParse = self.makeRecordParser(data)
            newRecord = self.makePaperRecord(
                code=recordParse.getPaperCode(),
                title=recordParse.getPaperTitle(),
                url=recordParse.getURL(),
            )
            yield newRecord

    def occurrences(self, responseXML) -> list:
        elements = etree.fromstring(responseXML)
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.getDataFromRecordRoot(record)
            recordParse = self.makeRecordParser(data)
            newRecord = self.makeOccurrenceRecord(
                paperCode=recordParse.getPaperCode(),
                date=recordParse.getDate(),
                url=recordParse.getURL(),
            )
            yield newRecord

    def numRecords(self, xml) -> int:
        xmlRoot = etree.fromstring(xml)
        numResults = xmlRoot.find(
            "{http://www.loc.gov/zing/srw/}numberOfRecords")
        if numResults is not None:
            return int(numResults.text)
        else:
            return 0

    def yearsPublished(self, xml) -> list:
        xmlRoot = etree.fromstring(xml)
        years = []
        for yearElement in xmlRoot.iter("year"):
            if yearElement is not None:
                year = yearElement.text
                if year.isdigit():
                    years.append(year)
        return years

    def onePaperTitleFromOccurrenceBatch(self, responseXML) -> str:
        elements = etree.fromstring(responseXML)
        recordsRoot = elements.find("{http://www.loc.gov/zing/srw/}records")
        if recordsRoot is None:
            print(repr(responseXML))
            return 'nonsense'
        record = recordsRoot[0]
        recordData = self.getDataFromRecordRoot(record)
        recordParser = self.makeRecordParser(recordData)
        return recordParser.getPaperTitle()

    def getDataFromRecordRoot(self, recordRoot):
        root = recordRoot[2]
        data = root[0]
        return data



