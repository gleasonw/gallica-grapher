class Query:

    def __init__(self, **kwargs):
        self.postInit(kwargs)

    def getFetchParams(self):
        raise NotImplementedError

    def postInit(self, kwargs):
        pass


class SRUQuery(Query):

    def __init__(self, **kwargs):
        self.startIndex = kwargs['startIndex']
        self.numRecords = kwargs['numRecords']
        self.cql = None
        self.codes = kwargs.get('codes')
        super().__init__(**kwargs)

    def getFetchParams(self):
        base = {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.startIndex,
            "maximumRecords": self.numRecords,
            "query": self.getCQL()
        }
        base.update(self.getCollapsingSetting())
        return base

    def getCQL(self):
        if not self.cql:
            self.cql = self.generateCQL()
        return self.cql

    def generateCQL(self):
        raise NotImplementedError

    def buildPaperCQL(self):
        if self.codes and self.codes[0]:
            formattedCodes = [f"{code}_date" for code in self.codes]
            return 'arkPress adj "' + '" or arkPress adj "'.join(formattedCodes) + '"'
        else:
            return "dc.type all \"fascicule\" and ocr.quality all \"Texte disponible\""

    def getCollapsingSetting(self):
        return {"collapsing": "false"}


class OccurrenceQuery(SRUQuery):

    def postInit(self, kwargs):
        self.startDate = kwargs['startDate']
        self.endDate = kwargs['endDate']
        self.term = kwargs['term']

        self.searchMetaData = kwargs['searchMetaData']
        self.linkDistance = self.searchMetaData.get('linkDistance', 10)
        self.linkTerm = self.searchMetaData.get('linkTerm')
        self.identifier = self.searchMetaData.get('identifier')

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
        cqlList = []
        (termCQL := self.buildTermCQL()) and cqlList.append(termCQL)
        (dateCQL := self.buildDateCQL()) and cqlList.append(dateCQL)
        (paperCQL := self.buildPaperCQL()) and cqlList.append(paperCQL)
        return ' and '.join(cqlList)

    def buildDateCQL(self):
        if self.startDate and self.endDate:
            return f'gallicapublication_date>="{self.startDate}" and gallicapublication_date<"{self.endDate}"'
        elif self.startDate:
            return f'gallicapublication_date="{self.startDate}"'
        else:
            return ''

    def buildTermCQL(self) -> str:
        if self.linkTerm:
            return f'text adj "{self.term}" prox/unit=word/distance={self.linkDistance} "{self.linkTerm}"'
        else:
            return f'text adj "{self.term}"'

    def __repr__(self):
        return f"Query({self.getCQL()})"


class ArkQueryForNewspaperYears(Query):

    def postInit(self, kwargs):
        self.ark = f'ark:/12148/{kwargs["code"]}/date'
        self.code = kwargs['code']

    def getCode(self):
        return self.code

    def getFetchParams(self):
        return {"ark": self.ark}

    def __repr__(self):
        return f'ArkQuery({self.ark})'


class PaperQuery(SRUQuery):

    def postInit(self, kwargs):
        self.codes = kwargs.get('codes') or []

    def generateCQL(self):
        return self.buildPaperCQL()

    def getCollapsingSetting(self):
        return {"collapsing": "true"}

    def getEssentialDataForMakingAQuery(self):
        return {"codes": self.codes}

    def __repr__(self):
        return f'PaperQuery({self.codes}, {self.startIndex}, {self.numRecords})'


class ContentQuery(Query):

    def postInit(self, kwargs):
        self.ark = kwargs['ark']
        self.term = kwargs['term']

    def getFetchParams(self):
        return {
            "ark": self.ark,
            "query": self.term
        }

    def __repr__(self):
        return f'OCRQuery({self.ark}, {self.term})'







