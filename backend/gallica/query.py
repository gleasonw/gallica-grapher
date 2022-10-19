class Query:

    def __init__(self, **kwargs):
        self.postInit(**kwargs)

    def getFetchParams(self):
        raise NotImplementedError

    def postInit(self, **kwargs):
        pass


class SRUQuery(Query):

    def __init__(self, **kwargs):
        super().__init__()
        self.startIndex = kwargs['startIndex']
        self.numRecords = kwargs['numRecords']
        self.collapsing = kwargs['collapsing']
        self.cql = None
        self.codes = None
        self.postInit(**kwargs)

    def postInit(self, **kwargs):
        pass

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

    def postInit(self, **kwargs):
        self.searchMetaData = kwargs['searchMetaData']
        self.linkDistance = self.searchMetaData.getLinkDistance()
        self.linkTerm = self.searchMetaData.getLinkTerm()
        self.startDate = kwargs['startDate']
        self.endDate = kwargs['endDate']
        self.term = kwargs['term']
        self.identifier = self.searchMetaData.getIdentifier()

    def getIdentifier(self):
        return self.identifier

    def getEssentialDataForMakingAQuery(self):
        return {
            "term": self.term,
            "endDate": self.endDate,
            "startDate": self.startDate,
            "codes": self.codes,
            "searchMetaData": self.searchMetaData
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

    def postInit(self, **kwargs):
        self.ark = f'ark:/12148/{kwargs["code"]}/date'
        self.code = kwargs['code']

    def getCode(self):
        return self.code

    def getFetchParams(self):
        return {"ark": self.ark}

    def __repr__(self):
        return f'ArkQuery({self.ark})'


class PaperQuery(SRUQuery):

    def postInit(self, **kwargs):
        self.collapsing = True

    def generateCQL(self):
        if self.codes:
            return self.buildPaperCQLfromQueryCodes()
        else:
            return "dc.type all \"fascicule\" and ocrquality > \"050.00\""

    def __repr__(self):
        return f'PaperQuery({self.codes}, {self.startIndex}, {self.numRecords})'


class OCRQuery(Query):

    def postInit(self, **kwargs):
        self.ark = kwargs['ark']
        self.term = kwargs['term']

    def getFetchParams(self):
        return {
            "ark": self.ark,
            "query": self.term
        }

    def __repr__(self):
        return f'OCRQuery({self.ark}, {self.term})'







