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

    def getQueries(self):
        return self.queries

    def setQueries(self, queries):
        self.queries = queries

    def setEstimateNumResults(self, estimateNumResults):
        self.estimateNumResults = estimateNumResults

    def setNumResultsRetrieved(self, numResultsRetrieved):
        self.numResultsRetrieved = numResultsRetrieved

    def __repr__(self):
        return f"Ticket({self.key}, {self.terms}, {self.codes}, {self.startYear}, {self.endYear}, {self.linkTerm}, {self.linkDistance})"