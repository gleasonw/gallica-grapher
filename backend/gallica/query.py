class Query:

    def __init__(
            self,
            cql=None,
            startIndex=None,
            numRecords=None,
            collapsing=None,
            term=None
    ):
        self.cql = cql
        self.startIndex = startIndex
        self.numRecords = numRecords
        self.collapsing = collapsing
        self.responseXML = None
        self.elapsedTime = None
        self.estimateNumRecordsToFetch = None
        self.term = term

    def handleResponse(self, data, elapsed):
        self.responseXML = data
        self.elapsedTime = elapsed

    def getParams(self):
        return{
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.startIndex,
            "maximumRecords": self.numRecords,
            "collapsing": self.collapsing,
            "query": self.cql,
        }


class NumOccurrencesForTermQuery(Query):

    def __init__(self, cql, term):
        super().__init__(
            cql=cql,
            startIndex=1,
            numRecords=1,
            collapsing=False,
            term=term
        )


class NumPapersOnGallicaQuery(Query):

    def __init__(self, cql):
        super().__init__(
            cql=cql,
            startIndex=1,
            numRecords=1,
            collapsing=True
        )


class PaperQuery(Query):

    def __init__(self, cql):
        super().__init__(
            cql=cql,
            startIndex=1,
            numRecords=1,
            collapsing=True
        )


class ArkQuery(Query):

    def __init__(self, code):
        super().__init__()
        self.ark = 'ark:/12148/cb32895690j/date'
        self.code = code

    def getParams(self):
        return {"ark": self.ark}




