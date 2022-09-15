class Query:

    def __init__(
            self,
            cql,
            startIndex,
            numRecords,
            collapsing,
            term=None
    ):
        self.cql = cql
        self.startIndex = startIndex
        self.numRecords = numRecords
        self.collapsing = collapsing
        self.responseXML = None
        self.elapsedTime = None
        self.term = term
