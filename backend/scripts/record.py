from lxml import etree
from scripts.date import Date


class Record:
    def __init__(self, root):
        record = root[2]
        self.recordData = record[0]
        self.valid = False
        self.paperCode = ''
        self.date = None
        self.url = ''
        self.paperTitle = None
        self.keyword = None
        self.ticketID = None

        self.parsePaperCodeFromXML()
        self.parseURLFromXML()

    def getPaperCode(self):
        return self.paperCode

    def getDate(self):
        pass

    def getUrl(self):
        return self.url

    def isValid(self):
        return self.valid

    def getPaperTitle(self):
        return self.paperTitle

    def setKeyword(self, keyword):
        self.keyword = keyword

    def setTicketID(self, ticketID):
        self.ticketID = ticketID

    def getKeyword(self):
        return self.keyword

    def getTicketID(self):
        return self.ticketID

    def parsePaperCodeFromXML(self):
        paperCodeElement = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}relation')

        if paperCodeElement is not None:
            elementText = paperCodeElement.text
            self.paperCode = elementText[-11:len(elementText)]

    def parseURLFromXML(self):
        urlElement = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}identifier')
        if urlElement is not None:
            self.url = urlElement.text

    def parseTitleFromXML(self):
        self.paperTitle = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}title').text

    def checkIfValid(self):
        if self.paperCode:
            self.valid = True


class KeywordRecord(Record):

    def __init__(self, root):
        super().__init__(root)
        self.parseDateFromXML()
        self.checkIfValid()

    def getDate(self):
        return self.date.getDate()

    def parseDateFromXML(self):
        dateElement = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            self.date = Date(dateElement.text)


class PaperRecord(Record):

    def __init__(self, root, gallicaSession):
        super().__init__(root)
        self.publishingYears = []
        self.publishingRange = [None, None]
        self.continuousRange = False
        self.session = gallicaSession

        self.checkIfValid()
        self.parseTitleFromXML()
        self.fetchYearsPublished()
        self.parseYears()
        self.checkIfYearsContinuous()
        self.generatePublishingRange()

    def isContinuous(self):
        return self.continuousRange

    def getDate(self):
        return self.publishingRange

    def fetchYearsPublished(self):
        paramsForArk = {'ark': f'ark:/12148/{self.paperCode}/date'}
        response = self.session.get(
            "",
            params=paramsForArk,
            timeout=15)
        try:
            root = etree.fromstring(response.content)
            for yearElement in root.iter("year"):
                if yearElement is not None:
                    year = yearElement.text
                    if year.isdigit():
                        self.publishingYears.append(int(year))
        except etree.XMLSyntaxError:
            pass

    def parseYears(self):
        if self.publishingYears:
            self.checkIfYearsContinuous()
            self.generatePublishingRange()

    def checkIfYearsContinuous(self):
        for i, year in enumerate(self.publishingYears):
            if i == len(self.publishingYears) - 1:
                self.continuousRange = True
                return
            nextYear = self.publishingYears[i + 1]
            if year + 1 != nextYear:
                return

    def generatePublishingRange(self):
        if self.publishingYears:
            lowYear = self.publishingYears[0]
            highYear = self.publishingYears[-1]
            self.publishingRange = [lowYear, highYear]
