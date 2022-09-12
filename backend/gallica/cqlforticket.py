from cqlSelectStringForPapers import CQLSelectStringForPapers


class CQLforTicket:

    def __init__(self):
        self.terms = None
        self.paperCodes = None
        self.startYear = None
        self.endYear = None

    def buildCQLstrings(self, options):
        self.startYear = options['startYear']
        self.endYear = options['endYear']
        self.terms = options['terms']
        self.paperCodes = options['paperCodes']
        cql = self.generateCQLforOptions()
        return cql

    def generateCQLforOptions(self):
        for term in self.terms:
            baseQuery = self.buildCQLforTerm(term)
            if self.paperCodes:
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
        baseQueryComponents.append('sortby dc.date/sort.ascending')
        baseQuery = " and ".join(baseQueryComponents)
        if self.paperCodes:
            baseQueryComponents.insert(0, '({formattedCodeString})')
        return baseQuery

    def buildCQLforPaperCodes(self, baseQuery):
        paperSelectCQLStrings = CQLSelectStringForPapers(self.paperCodes).cqlSelectStrings
        for codeString in paperSelectCQLStrings:
            yield baseQuery.format(formattedCodeString=codeString)

