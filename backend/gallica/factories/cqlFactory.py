NUM_CODES_PER_CQL = 4


class CQLFactory:

    def __init__(self):
        self.terms = None
        self.codes = None
        self.startYear = None
        self.endYear = None
        self.cqlForCodes = CQLStringForPaperCodes()

    def buildStringsForOptions(self, options):
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
        paperSelectCQLStrings = self.cqlForCodes.build(self.codes)
        for codeString in paperSelectCQLStrings:
            yield baseQuery.format(formattedCodeString=codeString)


class CQLStringForPaperCodes:
    def __init__(self, numCodesPerCQL=NUM_CODES_PER_CQL):
        self.numCodesPerCQL = numCodesPerCQL

    def build(self, codeChunks):
        cqlStrings = []
        for i in range(0, len(codeChunks), self.numCodesPerCQL):
            codeChunks = codeChunks[i:i + self.numCodesPerCQL]
            formattedCodes = [f"{code}_date" for code in codeChunks]
            CQLpaperSelectString = 'arkPress all "' + '" or arkPress all "'.join(
                formattedCodes) + '"'
            cqlStrings.append(CQLpaperSelectString)
        return cqlStrings



