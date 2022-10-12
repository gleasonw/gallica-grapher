class Query:

    def __init__(self, **kwargs):
        self.codes = kwargs.get("codes", [])
        self.linkDistance = kwargs.get("linkDistance", 0)
        self.linkTerm = kwargs.get("linkTerm", None)
        self.publicationStartDate = kwargs.get('publicationStartDate')
        self.publicationEndDate = kwargs.get('publicationEndDate')
        self.startIndex = kwargs.get('startIndex')
        self.numRecords = kwargs.get('numRecords')
        self.collapsing = kwargs.get('collapsing')
        self.term = kwargs.get('term')

        self.estimateNumRecordsToFetch = None
        self.code = None
        self.ark = None
        self.cql = None

    def getFetchParams(self):
        return{
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.startIndex,
            "maximumRecords": self.numRecords,
            "collapsing": self.collapsing,
            "query": self.getCQL(),
        }

    def getEssentialDataForMakingAQuery(self):
        return {
            "term": self.term,
            "publicationStartDate": self.publicationStartDate,
            "publicationEndDate": self.publicationEndDate,
            "codes": self.codes,
            "linkDistance": self.linkDistance,
            "linkTerm": self.linkTerm,
        }

    def getStartDate(self):
        return self.publicationStartDate

    def getCQL(self):
        if not self.cql:
            self.cql = self.generateCQL()
        return self.cql

    def generateCQL(self):
        termCQL = self.buildLinkedTermCQL() if self.linkTerm else self.buildTermCQL()
        dateCQL = self.buildDateCQL()
        paperCQL = f" and ({self.buildPaperCQL(self.codes)})" if self.codes else ""
        return f"({termCQL}) and ({dateCQL}){paperCQL} and (dc.type all \"fascicule\")"

    def buildDateCQL(self):
        return f'gallicapublication_date>="{self.publicationStartDate}" and gallicapublication_date<="{self.publicationEndDate}"'

    def buildTermCQL(self) -> str:
        return f'gallica adj "{self.term}"'

    def buildLinkedTermCQL(self):
        return f'text adj "{self.term}" prox/unit=word/distance={self.linkDistance} "{self.linkTerm}"'

    def buildPaperCQL(self, codes):
        formattedCodes = [f"{code}_date" for code in codes]
        return 'arkPress adj "' + '" or arkPress adj "'.join(formattedCodes) + '"'

    def __repr__(self):
        return f"Query({self.getCQL()})"


class ArkQueryForNewspaperYears(Query):

    def __init__(self, code):
        super().__init__()
        self.ark = f'ark:/12148/{code}/date'
        self.code = code

    def getCode(self):
        return self.code

    def getFetchParams(self):
        return {"ark": self.ark}

    def __repr__(self):
        return f'ArkQuery({self.ark})'


class PaperQuery(Query):

    def __init__(self, startIndex, numRecords, codes=None):
        super().__init__(
            codes=codes,
            startIndex=startIndex,
            numRecords=numRecords,
            collapsing=True)

    def generateCQL(self):
        if self.codes:
            return self.buildPaperCQL(self.codes)
        else:
            return "dc.type all \"fascicule\" and ocrquality > \"050.00\""

    def __repr__(self):
        return f'PaperQuery({self.codes}, {self.startIndex}, {self.numRecords})'


class OCRQuery(Query):

    def __init__(self, paperCode, term):
        super().__init__()
        self.ark = paperCode
        self.term = term

    def getFetchParams(self):
        return {
            "ark": self.ark,
            "query": self.term
        }

    def __repr__(self):
        return f'OCRQuery({self.ark}, {self.term})'







