from lxml import etree
import re


class Record:

    @staticmethod
    def standardizeDate(date):
        yearMonDay = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        twoYears = re.compile(r"^\d{4}-\d{4}$")
        oneYear = re.compile(r"^\d{4}$")
        oneYearOneMon = re.compile(r"^\d{4}-\d{2}$")
        if not yearMonDay.match(date):
            if oneYear.match(date):
                return date + "-01-01"
            elif oneYearOneMon.match(date):
                return date + "-01"
            elif twoYears.match(date):
                dates = date.split("-")
                lowerDate = int(dates[0])
                higherDate = int(dates[1])
                if higherDate - lowerDate <= 10:
                    newDate = (lowerDate + higherDate) // 2
                    return str(newDate) + "-01-01"
                else:
                    return None
            else:
                return None
        else:
            return date

    def __init__(self, root):
        record = root[2]
        self.recordData = record[0]
        self.paper = ''
        self.date = ''
        self.identifier = ''
        self.getDateFromHit()
        self.getPaperFromHit()
        self.getIdentifierFromHit()

    def getPaper(self):
        return self.paper

    def getDate(self):
        return self.date

    def getIdentifier(self):
        return self.identifier

    def getDateFromHit(self):
        dateOfHit = self.recordData.find('{http://purl.org/dc/elements/1.1/}date').text

        self.date = Record.standardizeDate(dateOfHit)

    def getPaperFromHit(self):
        journalOfHit = self.recordData.find('{http://purl.org/dc/elements/1.1/}relation').text
        if journalOfHit:
            self.paper = journalOfHit[-11:len(journalOfHit)]

    def getIdentifierFromHit(self):
        identifierOfHit = self.recordData.find('{http://purl.org/dc/elements/1.1/}identifier').text
        self.identifier = identifierOfHit
