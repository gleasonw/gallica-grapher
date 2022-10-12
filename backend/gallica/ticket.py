NUM_CODES_PER_BUNDLE = 10


class Ticket:

    def __init__(
            self,
            key,
            terms,
            codes,
            dateRange,
            linkTerm,
            linkDistance,
            fetchType
    ):
        self.key = key
        self.terms = terms
        self.codes = codes
        self.startYear = dateRange[0]
        self.endYear = dateRange[1]
        self.queries = None
        self.estimateNumResults = 0
        self.numResultsRetrieved = 0
        self.linkTerm = linkTerm
        self.linkDistance = linkDistance
        self.fetchType = fetchType

    def getID(self):
        return self.key

    def getTerms(self):
        return self.terms

    def getLinkTerm(self):
        return self.linkTerm

    def getLinkDistance(self):
        return self.linkDistance

    def getStartDate(self):
        return self.startYear

    def getEndDate(self):
        return self.endYear

    def getFetchType(self):
        return self.fetchType

    def getDateGroupings(self):
        groupings = {
            'all': [(f"{self.startYear}-01-01", f"{self.endYear + 1}-01-01")],
            'year': self.makeYearGroupings(),
            'month': self.makeMonthGroupings()
        }
        return groupings[self.fetchType]

    def makeYearGroupings(self):
        yearGroups = set()
        for year in range(self.startYear, self.endYear + 1):
            yearGroups.add((f"{year}-01-01", f"{year + 1}-01-01"))
        return yearGroups

    def makeMonthGroupings(self):
        monthGroups = set()
        for year in range(self.startYear, self.endYear + 1):
            for month in range(1, 13):
                if month == 12:
                    monthGroups.add((f"{year}-{month:02}-01", f"{year + 1}-01-01"))
                else:
                    monthGroups.add((f"{year}-{month:02}-01", f"{year}-{month + 1:02}-01"))
        return monthGroups

    def getCodeBundles(self):
        return [] if self.codes is None else [
            self.codes[i:i+NUM_CODES_PER_BUNDLE]
            for i in range(0, len(self.codes), NUM_CODES_PER_BUNDLE)
        ]

    def __repr__(self):
        return f"Ticket({self.key}, {self.terms}, {self.codes}, {self.startYear}, {self.endYear}, {self.linkTerm}, {self.linkDistance})"