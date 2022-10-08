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

    def getPaperCodes(self):
        return self.codes

    def getID(self):
        return self.key

    def getGroupingIntervals(self):
        groupings = {
            'year': set(zip(
                range(self.startYear, self.endYear + 1),
                range(self.startYear, self.endYear + 1)
            )),
            'month': [
                (f"{year}-{month:02}-01", f"{year}-{month:02}-31")
                for year in range(self.startYear, self.endYear + 1)
                for month in range(1, 13)
            ]
        }
        return groupings[self.fetchType]

    def getCodeBundles(self):
        return None if self.codes is None else [
            self.codes[i:i+NUM_CODES_PER_BUNDLE]
            for i in range(0, len(self.codes), NUM_CODES_PER_BUNDLE)
        ]

    def __repr__(self):
        return f"Ticket({self.key}, {self.terms}, {self.codes}, {self.startYear}, {self.endYear}, {self.linkTerm}, {self.linkDistance})"