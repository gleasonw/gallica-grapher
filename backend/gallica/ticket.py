class Ticket:

    def __init__(
            self,
            key,
            terms,
            codes,
            startYear,
            endYear,
    ):
        self.key = key
        self.terms = terms
        self.codes = codes
        self.startYear = startYear
        self.endYear = endYear
        self.queries = None
        self.estimateNumResults = 0
        self.numResultsRetrieved = 0

    def setQueries(self, queries):
        self.queries = queries

    def setEstimateNumResults(self, estimateNumResults):
        self.estimateNumResults = estimateNumResults

    def setNumResultsRetrieved(self, numResultsRetrieved):
        self.numResultsRetrieved = numResultsRetrieved
