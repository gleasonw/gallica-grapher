NUM_CODES_PER_CQL = 4


class CQLFactory:

    def __init__(self):
        self.ticket = None
        self.cqlForCodes = CQLStringForPaperCodes()

    def buildStringsForTicket(self, ticket):
        self.ticket = ticket
        if self.ticket.codes:
            cql = self.generateCQLforCodesAndTerms()
        else:
            cql = self.generateCQLforTerms()
        return cql

    def generateCQLforCodesAndTerms(self):
        termCQL = {}
        for term in self.ticket.terms:
            baseQuery = self.buildCQLforTerm(term)
            termCQL[term] = (
                baseQuery.format(formattedCodeString=code)
                for code in self.ticket.codes
            )
        return termCQL

    def generateCQLforTerms(self):
        termCQL = {}
        for term in self.ticket.terms:
            termCQL[term] = [self.buildCQLforTerm(term)]
        return termCQL

    def buildCQLforTerm(self, term):
        baseQueryComponents = []
        if self.ticket.startYear and self.ticket.endYear:
            baseQueryComponents.append(f'dc.date >= "{self.ticket.startYear}"')
            baseQueryComponents.append(f'dc.date <= "{self.ticket.endYear}"')
        baseQueryComponents.append(f'(gallica adj "{term}")')
        baseQueryComponents.append('(dc.type adj "fascicule")')
        if self.ticket.codes:
            baseQueryComponents.insert(0, '({formattedCodeString})')
        baseQuery = " and ".join(baseQueryComponents)
        baseQuery = f'{baseQuery} sortby dc.date/sort.ascending'
        return baseQuery

    def buildCQLforPaperCodes(self, baseQuery):
        paperSelectCQLStrings = self.cqlForCodes.build(self.ticket.codes)
        for codeString in paperSelectCQLStrings:
            yield baseQuery.format(formattedCodeString=codeString)


class CQLStringForPaperCodes:
    def __init__(self, numCodesPerCQL=NUM_CODES_PER_CQL):
        self.numCodesPerCQL = numCodesPerCQL

    def build(self, codes):
        cqlStrings = []
        for i in range(0, len(codes), self.numCodesPerCQL):
            codeChunks = codes[i:i + self.numCodesPerCQL]
            formattedCodes = [f"{code}_date" for code in codeChunks]
            CQLpaperSelectString = 'arkPress adj "' + '" or arkPress adj "'.join(
                formattedCodes) + '"'
            cqlStrings.append(CQLpaperSelectString)
        return cqlStrings



