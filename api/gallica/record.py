from lxml import etree
import re

#TODO: Day, month, year for DB
class Record:
    def __init__(self, root):
        record = root[2]
        self.recordData = record[0]
        self.valid = None
        self.paperCode = ''
        self.dateText = ''
        self.yearMonDay = []
        self.url = ''
        self.parsePaperCodeFromXML()
        self.parseURLFromXML()

    def getPaperCode(self):
        return self.paperCode

    def getYearMonDay(self):
        return self.yearMonDay

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

    def parseDateFromXML(self):
        dateElement = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            self.date = dateElement.text
            self.decomposeDate()

    def checkIfValid(self):
        if self.date and self.paperCode:
            self.valid = True
        else:
            self.valid = False

    def decomposeDate(self):
        yearMonDay = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        oneYear = re.compile(r"^\d{4}$")
        oneYearOneMon = re.compile(r"^\d{4}-\d{2}$")
        if yearMonDay.match(self.date):
            splitDate = self.date.split('-')
            self.yearMonDay = [splitDate[0], splitDate[1], splitDate[2]]
        elif oneYearOneMon.match(self.date):
            splitDate = self.date.split('-')
            self.yearMonDay = [splitDate[0], splitDate[1], None]
        elif oneYear.match(self.date):
            self.yearMonDay = [self.date, None, None]
        else:
            self.yearMonDay = [None, None, None]


class PaperRecord(Record):

    def __init__(self, root, gallicaSession):
        super().__init__(root)
        self.title = ''
        self.publishingYears = []
        self.continuousRange = None
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

    #TODO: Could this be really slow?
    def fetchYearsPublished(self):
        paramsForArk = {'ark': f'ark:/12148/{self.paperCode}/date'}
        response = self.session.get("",
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
        else:
            self.date = [None, None]

    def checkIfYearsContinuous(self):
        for i, year in enumerate(self.publishingYears):
            if i == len(self.publishingYears) - 1:
                self.continuousRange = True
                return
            nextYear = self.publishingYears[i + 1]
            if year + 1 != nextYear:
                self.continuousRange = False
                return

    def generateAvailableRange(self):
        if self.publishingYears:
            lowYear = self.publishingYears[0]
            highYear = self.publishingYears[-1]
            self.date = [lowYear, highYear]

    def parseTitleFromXML(self):
        self.title = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}title').text

    def checkIfValid(self):
        if self.paperCode:
            self.valid = True
        else:
            self.valid = False
