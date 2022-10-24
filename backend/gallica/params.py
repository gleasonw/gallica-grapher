from gallica.date import Date
NUM_CODES_PER_BUNDLE = 10


class Params:

    def __init__(self, **kwargs):
        self.terms = kwargs['terms']
        self.codes = kwargs.get('codes') or []
        self.startDate = Date(kwargs.get('startDate')) if kwargs.get('startDate') else None
        self.endDate = Date(kwargs.get('endDate')) if kwargs.get('endDate') else self.startDate
        self.link = (kwargs.get('linkTerm'), kwargs.get('linkDistance'))
        self.grouping = kwargs['grouping']
        self.numRecords = kwargs.get('numRecords', 50)
        self.startIndex = kwargs.get('startIndex', 0)
        self.identifier = kwargs.get('identifier')

    def getLinkDistance(self):
        return self.link[1]

    def getNumRecords(self):
        return self.numRecords

    def getTerms(self):
        return self.terms

    def getStartIndex(self):
        return self.startIndex

    def getIdentifier(self):
        return self.identifier

    def getGrouping(self):
        return self.grouping

    def endYearInt(self):
        return int(self.endDate.getYear())

    def startYearInt(self):
        return int(self.startDate.getYear())

    def getYearRangeLength(self):
        return self.endYearInt() + 1 - self.startYearInt()

    def getCodeBundles(self):
        return [] if self.codes is None else [
            self.codes[i:i+NUM_CODES_PER_BUNDLE]
            for i in range(0, len(self.codes), NUM_CODES_PER_BUNDLE)
        ]

    def getLinkTerm(self):
        return self.link[0]

    def getDateGroupings(self):
        if self.startDate is None and self.endDate is None:
            return [(None, None)]
        groupings = {
            'all': self.makeWideGroupingsForAllSearch,
            'year': self.makeYearGroupings,
            'month': self.makeMonthGroupings
        }
        dates = groupings[self.grouping]()
        return dates

    def makeWideGroupingsForAllSearch(self):
        if self.startDate.getDay():
            return [(self.startDate.getDateText(), None)]
        elif month := self.startDate.getMonth():
            nextYear = self.startYearInt() + 1 if month == '12' else self.startDate.getYear()
            nextMonth = (int(month) + 1) % 12
            return [(
                f"{self.startDate.getYear()}-{int(self.startDate.getMonth()):02}-01",
                f"{nextYear}-{nextMonth:02}-01"
            )]
        else:
            return [(
                f"{self.startDate.getYear()}-01-01",
                f"{self.endYearInt() + 1}-01-01"
            )]

    def makeYearGroupings(self):
        yearGroups = set()
        for year in range(self.startYearInt(), self.endYearInt() + 1):
            yearGroups.add((f"{year}-01-01", f"{year + 1}-01-01"))
        return yearGroups

    def makeMonthGroupings(self):
        monthGroups = set()
        for year in range(self.startYearInt(), self.endYearInt() + 1):
            for month in range(1, 13):
                if month == 12:
                    monthGroups.add((f"{year}-{month:02}-01", f"{year + 1}-01-01"))
                else:
                    monthGroups.add((f"{year}-{month:02}-01", f"{year}-{month + 1:02}-01"))
        return monthGroups

    def __repr__(self):
        return f"Params({self.terms}, {self.codes}, {self.startDate}, {self.endDate}, {self.getLinkTerm()}, {self.getLinkDistance()})"
