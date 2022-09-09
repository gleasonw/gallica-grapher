class Query:

    def __init__(
            self,
            url,
            startIndex,
            numRecords,
            collapsing
    ):
        self.url = url
        self.startIndex = startIndex
        self.numRecords = numRecords
        self.collapsing = collapsing
