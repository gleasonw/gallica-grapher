class Query:

    def __init__(self, **kwargs):
        self.cql = kwargs.get('cql')
        self.startIndex = kwargs.get('startIndex')
        self.numRecords = kwargs.get('numRecords')
        self.collapsing = kwargs.get('collapsing')
        self.term = kwargs.get('term')
        self.responseXML = None
        self.elapsedTime = None
        self.estimateNumRecordsToFetch = None

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

    def __repr__(self):
        return f'NumOccurrencesForTermQuery({self.cql}, {self.term})'


class NumPapersOnGallicaQuery(Query):

    def __init__(self, cql):
        super().__init__(
            cql=cql,
            startIndex=1,
            numRecords=1,
            collapsing=True
        )

    def __repr__(self):
        return f'NumPapersOnGallicaQuery({self.cql})'


class PaperQuery(Query):

    def __init__(self, cql, startIndex):
        super().__init__(
            cql=cql,
            startIndex=startIndex,
            numRecords=50,
            collapsing=True
        )

    def __repr__(self):
        return f'PaperQuery({self.cql})'


class ArkQuery(Query):

    def __init__(self, code):
        super().__init__()
        self.ark = f'ark:/12148/{code}/date'
        self.code = code

    def getParams(self):
        return {"ark": self.ark}

    def __repr__(self):
        return f'ArkQuery({self.ark})'




