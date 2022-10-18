class Query:

    def __init__(self):
        pass

    def getFetchParams(self):
        raise NotImplementedError


class SRUQuery(Query):

    def __init__(self, startIndex, numRecords, collapsing, codes):
        super().__init__()
        self.startIndex = startIndex
        self.numRecords = numRecords
        self.collapsing = collapsing
        self.cql = None
        self.codes = codes
        self.term = None
        self.linkTerm = None
        self.linkDistance = None
        self.startDate = None
        self.endDate = None

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

    def getCQL(self):
        if not self.cql:
            self.cql = self.generateCQL()
        return self.cql

    def generateCQL(self):
        raise NotImplementedError

    def buildPaperCQLfromQueryCodes(self):
        formattedCodes = [f"{code}_date" for code in self.codes]
        return 'arkPress adj "' + '" or arkPress adj "'.join(formattedCodes) + '"'


class OccurrenceQuery(SRUQuery):

    def __init__(
            self,
            codes,
            term,
            startIndex,
            numRecords,
            collapsing,
            startDate,
            endDate,
            requestMetaData
    ):
        super().__init__(
            startIndex=startIndex,
            numRecords=numRecords,
            collapsing=collapsing,
            codes=codes
        )
        self.linkDistance = requestMetaData.getLinkDistance()
        self.linkTerm = requestMetaData.getLinkTerm()
        self.startDate = startDate
        self.endDate = endDate
        self.term = term
        self.bundle = requestMetaData
        self.identifier = requestMetaData.getIdentifier()

    def getIdentifier(self):
        return self.identifier

    def getEssentialDataForMakingAQuery(self):
        return {
            "term": self.term,
            "endDate": self.endDate,
            "startDate": self.startDate,
            "codes": self.codes,
            "metadata": self.bundle
        }

    def getStartDate(self):
        return self.startDate

    def generateCQL(self):
        termCQL = self.buildLinkedTermCQL() if self.linkTerm else self.buildTermCQL()
        dateCQL = self.buildDateCQL()
        paperCQL = self.buildPaperCQLfromQueryCodes() if self.codes else "dc.type all \"fascicule\" and ocr.quality all \"Texte disponible\""
        return f"{termCQL} and {dateCQL} and ({paperCQL})"

    def buildDateCQL(self):
        return f'gallicapublication_date>="{self.startDate}" and gallicapublication_date<"{self.endDate}"'

    def buildTermCQL(self) -> str:
        return f'text adj "{self.term}"'

    def buildLinkedTermCQL(self):
        return f'text adj "{self.term}" prox/unit=word/distance={self.linkDistance} "{self.linkTerm}"'

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


class PaperQuery(SRUQuery):

    def __init__(self, startIndex, numRecords, codes=None):
        super().__init__(
            startIndex=startIndex,
            numRecords=numRecords,
            collapsing=True,
            codes=codes
        )

    def generateCQL(self):
        if self.codes:
            return self.buildPaperCQLfromQueryCodes()
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







