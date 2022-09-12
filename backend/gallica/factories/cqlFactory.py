NUM_CODES_PER_CQL = 4


class CQLFactory:

    def __init__(self):
        self.terms = None
        self.codes = None
        self.startYear = None
        self.endYear = None

    def buildCQLstrings(self, options):
        self.startYear = options['startYear']
        self.endYear = options['endYear']
        self.terms = options['terms']
        self.codes = list(map(
            lambda x: (x['code']),
            options['papersAndCodes']
        ))
        cql = self.generateCQLforOptions()
        return cql

    def generateCQLforOptions(self):
        for term in self.terms:
            baseQuery = self.buildCQLforTerm(term)
            if self.codes:
                yield from self.buildCQLforPaperCodes(baseQuery)
            else:
                yield baseQuery

    def buildCQLforTerm(self, term):
        baseQueryComponents = []
        if self.startYear and self.endYear:
            baseQueryComponents.append(f'dc.date >= "{self.startYear}"')
            baseQueryComponents.append(f'dc.date <= "{self.endYear}"')
        baseQueryComponents.append(f'(gallica adj "{term}")')
        baseQueryComponents.append('(dc.type adj "fascicule")')
        if self.codes:
            baseQueryComponents.insert(0, '({formattedCodeString})')
        baseQuery = " and ".join(baseQueryComponents)
        baseQuery = f'{baseQuery} sortby dc.date/sort.ascending'
        return baseQuery

    def buildCQLforPaperCodes(self, baseQuery):
        paperSelectCQLStrings = CQLSelectStringForPapers(self.codes).cqlSelectStrings
        for codeString in paperSelectCQLStrings:
            yield baseQuery.format(formattedCodeString=codeString)



class CQLSelectStringForPapers:
    def __init__(self, codes, numCodesPerCQL=NUM_CODES_PER_CQL):
        self.numCodesPerCQL = numCodesPerCQL
        self.codes = codes
        self.cqlSelectStrings = self.generatePaperCQLWithMaxNUM_CODESCodesEach()

    def generatePaperCQLWithMaxNUM_CODESCodesEach(self):
        cql20CodeStrings = []
        for i in range(0, len(self.codes), self.numCodesPerCQL):
            codes = self.codes[i:i + self.numCodesPerCQL]
            formattedCodes = [f"{code}_date" for code in codes]
            CQLpaperSelectString = 'arkPress all "' + '" or arkPress all "'.join(
                formattedCodes) + '"'
            cql20CodeStrings.append(CQLpaperSelectString)
        return cql20CodeStrings



