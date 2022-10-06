class Query:

    def __init__(self, **kwargs):
        self.codes = kwargs.get("codes", [])
        self.linkDistance = kwargs.get("linkDistance", 0)
        self.linkTerm = kwargs.get("linkTerm", None)
        self.cql = None
        self.startIndex = kwargs.get('startIndex')
        self.numRecords = kwargs.get('numRecords')
        self.collapsing = kwargs.get('collapsing')
        self.term = kwargs.get('term')
        self.estimateNumRecordsToFetch = None
        self.code = None
        self.ark = None
        self.publicationStartDate = kwargs.get('publicationStartDate')
        self.publicationEndDate = kwargs.get('publicationEndDate')
        self.buildPaperCQL = kwargs.get('buildPaperCQL')

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

    def getCQL(self):
        if not self.cql:
            self.cql = self.generateCQL()
        return self.cql

    def generateCQL(self):
        termCQL = self.buildLinkedTermCQL() if self.linkTerm else self.buildTermCQL()
        dateCQL = self.buildDateCQL()
        paperCQL = f" and {self.buildPaperCQL(self.codes)}" if self.codes else ""
        return f"({termCQL}) and ({dateCQL}){paperCQL} and (dc.type all \"fascicule\")"

    def buildDateCQL(self):
        return f'(gallicapublication_date="{self.publicationStartDate}" and gallicapublication_date="{self.publicationEndDate}")'

    def buildTermCQL(self) -> str:
        return f'(gallica adj "{self.term}")'

    def buildLinkedTermCQL(self):
        return f'(text adj "{self.term}" prox/unit=word/distance={self.linkDistance} "{self.linkTerm}")'

    def buildPaperCQL(self, codes):
        formattedCodes = [f"{code}_date" for code in codes]
        return 'arkPress adj "' + '" or arkPress adj "'.join(formattedCodes) + '"'


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


class ArkQueryForNewspaperYears(Query):

    def __init__(self, code):
        super().__init__()
        self.ark = f'ark:/12148/{code}/date'
        self.code = code

    def getParams(self):
        return {"ark": self.ark}

    def __repr__(self):
        return f'ArkQuery({self.ark})'


class OCRQuery(Query):

    def __init__(self, ark, term):
        super().__init__()
        self.ark = ark
        self.term = term

    def getParams(self):
        return {
            "ark": self.ark,
            "query": self.term
        }

    def __repr__(self):
        return f'OCRQuery({self.ark}, {self.term})'







