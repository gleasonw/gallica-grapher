from cqlSelectStringForPapers import CQLSelectStringForPapers


class CQLforTicket:

    def __init__(self):
        self.terms = None
        self.paperCodes = None
        self.startYear = None
        self.endYear = None
        self.baseQueryComponents = []

    def buildUrls(self, options):
        self.startYear = options['startYear']
        self.endYear = options['endYear']
        self.terms = options['terms']
        self.paperCodes = options['paperCodes']
        queries = self.generateCQLforOptions()
        return queries

    def generateCQLforOptions(self):
        for term in self.terms:
            baseQuery = self.buildCQLforTerm(term)
            if self.paperCodes:
                yield from self.buildCQLforPaperCodes(baseQuery)
            else:
                yield baseQuery

    def buildCQLforTerm(self, term):
        if self.startYear and self.endYear:
            self.baseQueryComponents.append(f'dc.date >= "{self.startYear}"')
            self.baseQueryComponents.append(f'dc.date <= "{self.endYear}"')
        self.baseQueryComponents.append(f'(gallica adj "{term}")')
        self.baseQueryComponents.append('(dc.type adj "fascicule")')
        self.baseQueryComponents.append('sortby dc.date/sort.ascending')
        baseQuery = " and ".join(self.baseQueryComponents)
        if self.paperCodes:
            self.baseQueryComponents.insert(0, '({formattedCodeString})')
        return baseQuery

    def buildCQLforPaperCodes(self, baseQuery):
        paperSelectCQLStrings = CQLSelectStringForPapers(self.paperCodes).cqlSelectStrings
        for codeString in paperSelectCQLStrings:
            yield baseQuery.format(formattedCodeString=codeString)

