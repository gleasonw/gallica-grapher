NUM_CODES_PER_BUNDLE = 10


class Params:

    def __init__(self,
                 terms,
                 codes,
                 startDate,
                 endDate,
                 link,
                 grouping,
                 numRecords=50,
                 startIndex=0,
                 identifier=None
                 ):
        self.terms = terms
        self.codes = codes
        self.startDate = int(startDate)
        self.endDate = int(endDate)
        self.link = link
        self.grouping = grouping
        self.numRecords = numRecords
        self.startIndex = startIndex
        self.identifier = identifier

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

    def getCodeBundles(self):
        return [] if self.codes is None else [
            self.codes[i:i+NUM_CODES_PER_BUNDLE]
            for i in range(0, len(self.codes), NUM_CODES_PER_BUNDLE)
        ]

    def getLinkTerm(self):
        return self.link[0]

    def getDateGroupings(self):
        groupings = {
            'all': self.makeAllGroupings,
            'year': self.makeYearGroupings,
            'month': self.makeMonthGroupings
        }
        dates = groupings[self.grouping]()
        return dates

    def makeAllGroupings(self):
        return [(f"{self.startDate}-01-01", f"{self.endDate + 1}-01-01")]

    def makeYearGroupings(self):
        yearGroups = set()
        for year in range(self.startDate, self.endDate + 1):
            yearGroups.add((f"{year}-01-01", f"{year + 1}-01-01"))
        return yearGroups

    def makeMonthGroupings(self):
        monthGroups = set()
        for year in range(self.startDate, self.endDate + 1):
            for month in range(1, 13):
                if month == 12:
                    monthGroups.add((f"{year}-{month:02}-01", f"{year + 1}-01-01"))
                else:
                    monthGroups.add((f"{year}-{month:02}-01", f"{year}-{month + 1:02}-01"))
        return monthGroups

    def __repr__(self):
        return f"Params({self.terms}, {self.codes}, {self.startDate}, {self.endDate}, {self.getLinkTerm()}, {self.getLinkDistance()}"
