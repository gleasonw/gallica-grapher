import re


class DateParse:

    def __init__(self, dateText):
        self.year = None
        self.month = None
        self.day = None
        self.dateText = dateText
        self.parseDateText()

    def getDate(self):
        return [
            self.year,
            self.month,
            self.day
        ]

    # TODO: Parse suspect dates, add that as a column
    def parseDateText(self):
        yearMonDay = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")
        oneYear = re.compile(r"^\d{4}$")
        oneYearOneMon = re.compile(r"^\d{4}-\d{1,2}$")
        if yearMonDay.match(self.dateText):
            self.setYearMonDay()
        elif oneYearOneMon.match(self.dateText):
            self.setYearMon()
        elif oneYear.match(self.dateText):
            self.setYear()
        else:
            pass

    def setYearMonDay(self):
        splitDate = self.dateText.split('-')
        self.year = splitDate[0]
        self.month = splitDate[1]
        self.day = splitDate[2]

    def setYearMon(self):
        splitDate = self.dateText.split('-')
        self.year = splitDate[0]
        self.month = splitDate[1]

    def setYear(self):
        self.year = self.dateText
