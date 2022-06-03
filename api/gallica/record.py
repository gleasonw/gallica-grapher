from lxml import etree
import re


class Record:

    def __init__(self, root):
        record = root[2]
        self.recordData = record[0]
        self.paperCode = ''
        self.date = ''
        self.url = ''
        self.parseDateFromXML()
        self.parsePaperCodeFromXML()
        self.parseURLFromXML()

    def getPaperCode(self):
        return self.paperCode

    def getDate(self):
        return self.date

    def getUrl(self):
        return self.url

    def parseDateFromXML(self):
        self.date = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}date').text
        self.standardizeDate()

    def parsePaperCodeFromXML(self):
        paperCode = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}relation').text

        if paperCode:
            self.paperCode = paperCode[-11:len(paperCode)]

    def parseURLFromXML(self):
        self.url = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}identifier').text

    def standardizeDate(self):
        yearMonDay = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not yearMonDay.match(self.date):
            self.fillDateGap()

    def fillDateGap(self):
        twoYears = re.compile(r"^\d{4}-\d{4}$")
        oneYear = re.compile(r"^\d{4}$")
        oneYearOneMon = re.compile(r"^\d{4}-\d{2}$")
        if oneYear.match(self.date):
            self.date += "-01-01"
        elif oneYearOneMon.match(self.date):
            self.date += "-01"
        elif twoYears.match(self.date):
            self.averageYearsAsNewDate()
        else:
            self.date = None

    def averageYearsAsNewDate(self):
        dates = self.date.split("-")
        lowerDate = int(dates[0])
        higherDate = int(dates[1])
        if higherDate - lowerDate <= 10:
            newDate = (lowerDate + higherDate) // 2
            self.date = str(newDate) + "-01-01"
        else:
            self.date = None


class PaperRecord(Record):

    def __init__(self, root):
        super().__init__(root)
        self.title = ''
        self.parseTitleFromXML()

    def getTitle(self):
        return self.title

    def parseTitleFromXML(self):
        self.title = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}title').text

    def parseDateFromXML(self):
        self.date = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}date').text



