from cqlSelectStringForPapers import CQLSelectStringForPapers


#TODO: build as many urls as there are terms!
class UrlsForTicket:

    def __init__(self):
        self.keyword = None
        self.paperCodes = None
        self.startYear = None
        self.endYear = None
        self.baseQueryComponents = []

    def buildUrls(self, options):
        self.startYear = options['startYear']
        self.endYear = options['endYear']
        self.keyword = options['keyword']
        self.paperCodes = options['paperCodes']
        queries = self.generateCQLforOptions()
        return queries

    def generateCQLforOptions(self):
        if self.startYear and self.endYear:
            self.baseQueryComponents.append(f'dc.date >= "{self.startYear}"')
            self.baseQueryComponents.append(f'dc.date <= "{self.endYear}"')
        self.baseQueryComponents.append(f'(gallica adj "{self.keyword}")')
        self.baseQueryComponents.append('(dc.type adj "fascicule")')
        self.baseQueryComponents.append('sortby dc.date/sort.ascending')
        baseQuery = " and ".join(self.baseQueryComponents)
        if self.paperCodes:
            self.baseQueryComponents.insert(0, '({formattedCodeString})')
            return self.buildURLsforPaperCodes(baseQuery)
        else:
            yield baseQuery

    def buildURLsforPaperCodes(self, baseQuery):
        paperSelectCQLStrings = CQLSelectStringForPapers(self.paperCodes).cqlSelectStrings
        for codeString in paperSelectCQLStrings:
            yield baseQuery.format(formattedCodeString=codeString)

