from lxml import etree
from gallicaGetter.date import Date


class GallicaXMLparse:

    def getOnePaperFromRecordBatch(self, responseXML) -> str:
        records = self.getRecordsFromXML(responseXML)
        if records:
            return self.getPaperTitleFromRecord(records[0])
        else:
            return ''

    def getNumResultsAndPagesForOccurrenceInPeriodical(self, responseXML) -> tuple:
        elements = etree.fromstring(responseXML)
        topLevel = elements.find('.')
        numResults = topLevel.attrib.get('countResults')
        items = topLevel[1].findall('item')
        pagesWithContents = self.getPageAndContextForOccurrence(items)
        return numResults, pagesWithContents

    def getRecordsFromXML(self, xml) -> list:
        elements = etree.fromstring(xml)
        recordsRoot = elements.find("{http://www.loc.gov/zing/srw/}records")
        if recordsRoot is None:
            return []
        return recordsRoot.findall("{http://www.loc.gov/zing/srw/}record")

    @staticmethod
    def getNumRecords(xml) -> int:
        xmlRoot = etree.fromstring(xml)
        numResults = xmlRoot.find(
            "{http://www.loc.gov/zing/srw/}numberOfRecords")
        if numResults is not None:
            return int(numResults.text)
        else:
            return 0

    @staticmethod
    def getYearsPublished(xml) -> list:
        xmlRoot = etree.fromstring(xml)
        years = [
            GallicaXMLparse.getYearFromElement(yearElement)
            for yearElement in xmlRoot.iter("year")
        ]
        return list(filter(None, years))

    @staticmethod
    def getYearFromElement(yearElement):
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

    @staticmethod
    def getPaperCodeFromRecord(record) -> str:
        xml = GallicaXMLparse.getDataFromRecordRoot(record)
        paperCodeElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}relation')
        if paperCodeElement is not None:
            elementText = paperCodeElement.text
            paperCode = elementText[-11:len(elementText)]
            return paperCode
        else:
            return 'None'

    @staticmethod
    def getURLfromRecord(record) -> str:
        xml = GallicaXMLparse.getDataFromRecordRoot(record)
        urlElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}identifier')
        if urlElement is not None:
            url = urlElement.text
            return url

    @staticmethod
    def getPaperTitleFromRecord(record) -> str:
        xml = GallicaXMLparse.getDataFromRecordRoot(record)
        paperTitle = xml.find(
            '{http://purl.org/dc/elements/1.1/}title').text
        return paperTitle

    @staticmethod
    def getDateFromRecord(record) -> Date:
        xml = GallicaXMLparse.getDataFromRecordRoot(record)
        dateElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            return Date(dateElement.text)

    @staticmethod
    def getPageAndContextForOccurrence(itemsXML) -> list:
        items = []
        for item in itemsXML:
            page = item.find('p_id')
            page = page.text if page is not None else None
            content = item.find('content')
            content = content.text if content is not None else None
            items.append((page, content))
        return items
