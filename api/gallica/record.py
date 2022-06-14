from lxml import etree
from gallica.date import Date


class Record:
    def __init__(self, root):
        record = root[2]
        self.recordData = record[0]
        self.valid = False
        self.paperCode = ''
        self.date = ''
        self.yearMonDay = []
        self.url = ''
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

    def parsePaperCodeFromXML(self):
        paperCode = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}relation').text

        if paperCode:
            self.paperCode = paperCode[-11:len(paperCode)]

    def parseURLFromXML(self):
        self.url = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}identifier').text

    def checkIfValid(self):
        pass


class KeywordRecord(Record):

    def __init__(self, root):
        super().__init__(root)
        self.parseDateFromXML()
        self.checkIfValid()

    def getDate(self):
        return self.date.getDate()

    def getJSTimestamp(self):
        return self.date.getJSTimestamp()

    def parseDateFromXML(self):
        dateElement = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            self.date = Date(dateElement.txt)

    def checkIfValid(self):
        if self.date and self.paperCode:
            self.valid = True


class PaperRecord(Record):

    def __init__(self, root, gallicaSession):
        super().__init__(root)
        self.title = ''
        self.publishingYears = []
        self.publishingRange = [None, None]
        self.continuousRange = False
        self.session = gallicaSession

        self.checkIfValid()
        self.parseTitleFromXML()
        self.fetchYearsPublished()
        self.parseYears()
        self.checkIfYearsContinuous()
        self.generateAvailableRange()

    def getTitle(self):
        return self.title

    def getContinuous(self):
        return self.continuousRange

    def getDate(self):
        return self.publishingRange

    def checkIfValid(self):
        if self.paperCode:
            self.valid = True

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
            self.generateAvailableRange()

    def checkIfYearsContinuous(self):
        for i, year in enumerate(self.publishingYears):
            if i == len(self.publishingYears) - 1:
                self.continuousRange = True
                return
            nextYear = self.publishingYears[i + 1]
            if year + 1 != nextYear:
                return

    def generateAvailableRange(self):
        if self.publishingYears:
            lowYear = str(self.publishingYears[0])
            highYear = str(self.publishingYears[-1])
            self.publishingRange = [lowYear, highYear]

    def parseTitleFromXML(self):
        self.title = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}title').text
