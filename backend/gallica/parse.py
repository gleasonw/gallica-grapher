from lxml import etree
from gallica.date import Date


class Parse:

    def __init__(self):
        pass

    def onePaperTitleFromOccurrenceBatch(self, responseXML) -> str:
        elements = etree.fromstring(responseXML)
        recordsRoot = elements.find("{http://www.loc.gov/zing/srw/}records")
        if recordsRoot is None:
            return 'nonsense'
        record = recordsRoot[0]
        recordData = self.getDataFromRecordRoot(record)
        return self.getPaperTitle(recordData)

    def OCRtext(self, responseXML) -> tuple:
        elements = etree.fromstring(responseXML)
        topLevel = elements.find('.')
        numResults = topLevel.attrib.get('countResults')
        items = topLevel[1].findall('item')
        pagesWithContents = self.getPageAndContent(items)
        return numResults, pagesWithContents

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
    def parseCodeFromArk(xml):
        arkElement = etree.fromstring(xml)
        if arkElement is not None:
            issuesElement = arkElement.find('.')
            if issuesElement is not None:
                issueURL = issuesElement.attrib.get('parentArk')
                return issueURL.split('/')[-2]
        else:
            return None

    @staticmethod
    def getDataFromRecordRoot(recordRoot):
        root = recordRoot[2]
        data = root[0]
        return data

    @staticmethod
    def getPaperCode(xml) -> str:
        paperCodeElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}relation')

        if paperCodeElement is not None:
            elementText = paperCodeElement.text
            paperCode = elementText[-11:len(elementText)]
            return paperCode
        else:
            return 'None'

    @staticmethod
    def getURL(xml) -> str:
        urlElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}identifier')
        if urlElement is not None:
            url = urlElement.text
            return url

    @staticmethod
    def getPaperTitle(xml) -> str:
        paperTitle = xml.find(
            '{http://purl.org/dc/elements/1.1/}title').text
        return paperTitle

    @staticmethod
    def getDate(xml) -> Date:
        dateElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            return Date(dateElement.text)

    @staticmethod
    def getPageAndContent(itemsXML) -> list:
        items = []
        for item in itemsXML:
            page = item.find('p_id')
            page = page.text if page is not None else None
            content = item.find('content')
            content = content.text if content is not None else None
            items.append((page, content))
        return items
