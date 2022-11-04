import re
import weakref


class Date:

    _cache = {}
    dateFormats = [
        re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$"),
        re.compile(r"^\d{4}-\d{1,2}$"),
        re.compile(r"^\d{4}$")
    ]

    @staticmethod
    def __new__(cls, dateText):
        dateText = str(dateText)
        selfref = Date._cache.get(dateText)
        if not selfref:
            self = super().__new__(cls)
            self.dateText = dateText
            self.date = Date.parseDateText(dateText)
            Date._cache[dateText] = weakref.ref(self)
        else:
            self = selfref()
        return self

    @staticmethod
    def parseDateText(dateText):
        date = [None, None, None]
        for dateFormat in Date.dateFormats:
            if dateFormat.match(dateText):
                for index, entry in enumerate(dateText.split('-')):
                    date[index] = entry
                return date
        return date

    def __init__(self, dateText):
        pass

    def __repr__(self):
        return f'Date({self.date})'

    def getDateAsList(self) -> list:
        return self.date

    def getDateText(self) -> str:
        return self.dateText

    def getYear(self) -> str:
        return self.date[0]

    def getMonth(self) -> str:
        return self.date[1]

    def getDay(self) -> str:
        return self.date[2]

    def __del__(self):
        del Date._cache[self.dateText]

