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
        self.parseRecord = recordParser

    def papers(self, responseXML) -> list:
        elements = etree.fromstring(responseXML)
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.getDataFromRecordRoot(record)
            newRecord = self.makePaperRecord(
                code=self.parseRecord.getPaperCode(data),
                title=self.parseRecord.getPaperTitle(data),
                url=self.parseRecord.getURL(data),
            )
            yield newRecord

    def occurrences(self, responseXML) -> list:
        elements = etree.fromstring(responseXML)
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.getDataFromRecordRoot(record)
            newRecord = self.makeOccurrenceRecord(
                paperCode=self.parseRecord.getPaperCode(data),
                date=self.parseRecord.getDate(data),
                url=self.parseRecord.getURL(data),
            )
            yield newRecord

    def onePaperTitleFromOccurrenceBatch(self, responseXML) -> str:
        elements = etree.fromstring(responseXML)
        recordsRoot = elements.find("{http://www.loc.gov/zing/srw/}records")
        if recordsRoot is None:
            return 'nonsense'
        record = recordsRoot[0]
        recordData = self.getDataFromRecordRoot(record)
        return self.parseRecord.getPaperTitle(recordData)

    @staticmethod
    def numRecords(xml) -> int:
        xmlRoot = etree.fromstring(xml)
        numResults = xmlRoot.find(
            "{http://www.loc.gov/zing/srw/}numberOfRecords")
        if numResults is not None:
            return int(numResults.text)
        else:
            return 0

    @staticmethod
    def yearsPublished(xml) -> list:
        xmlRoot = etree.fromstring(xml)
        years = [
            Parse.parseYearFromArk(yearElement)
            for yearElement in xmlRoot.iter("year")
        ]
        return list(filter(None, years))

    @staticmethod
    def parseYearFromArk(yearElement):
        if yearElement is not None:
            year = yearElement.text
            return year if year.isdigit() else None
        else:
            return None

    @staticmethod
    def getDataFromRecordRoot(recordRoot):
        root = recordRoot[2]
        data = root[0]
        return data



