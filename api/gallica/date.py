import datetime
import re

import ciso8601


class Date:

    @staticmethod
    def dateToTimestamp(date):
        dateObject = ciso8601.parse_datetime(date)
        timestamp = datetime.datetime.timestamp(dateObject) * 1000
        return timestamp

    def __init__(self, dateText):
        self.year = None
        self.month = None
        self.day = None
        self.jsTimestamp = None
        self.dateText = dateText
        self.parseDateText()

    def getDate(self):
        return [
            self.year,
            self.month,
            self.day
        ]

    def getJSTimestamp(self):
        return self.jsTimestamp

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
            self.setDateUnknown()

    def setYearMonDay(self):
        splitDate = self.dateText.split('-')
        self.year = splitDate[0]
        self.month = splitDate[1]
        self.day = splitDate[2]
        self.jsTimestamp = Date.dateToTimestamp(
            "-".join([
                self.year,
                self.getMonthTwoDigits(),
                self.getDayTwoDigits()
            ]))

    def setYearMon(self):
        splitDate = self.dateText.split('-')
        self.year = splitDate[0]
        self.month = splitDate[1]
        self.jsTimestamp = Date.dateToTimestamp(
            "-".join([
                self.year,
                self.getMonthTwoDigits(),
                "01"
            ]))

    def setYear(self):
        self.year = self.dateText
        self.jsTimestamp = Date.dateToTimestamp(
            "-".join([
                self.year,
                "01",
                "01"
            ]))

    def setDateUnknown(self):
        self.jsTimestamp = None

    def getMonthTwoDigits(self):
        if len(self.month) == 1:
            return f'0{self.month}'
        else:
            return self.month

    def getDayTwoDigits(self):
        if len(self.day) == 1:
            return f'0{self.day}'
        else:
            return self.day
