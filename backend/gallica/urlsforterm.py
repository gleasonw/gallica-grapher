from cqlSelectStringForPapers import CQLSelectStringForPapers


class UrlsForTerm:

    def __init__(
            self,
            searchTerm,
            startYear=None,
            endYear=None,
            paperCodes=None
    ):

        self.keyword = searchTerm
        self.startYear = startYear
        self.endYear = endYear
        self.baseQueryComponents = []
        self.paperCodes = paperCodes
        self.queries = []
        self.baseQuery = ''

        self.buildBaseQuery()

    def buildBaseQuery(self):
        if self.startYear and self.endYear:
            self.baseQueryComponents.append(f'dc.date >= "{self.startYear}"')
            self.baseQueryComponents.append(f'dc.date <= "{self.endYear}"')
        self.baseQueryComponents.append(f'(gallica adj "{self.keyword}")')
        self.baseQueryComponents.append('(dc.type adj "fascicule")')
        self.baseQueryComponents.append('sortby dc.date/sort.ascending')
        self.baseQuery = " and ".join(self.baseQueryComponents)
        self.queries.append(self.baseQuery)
        if self.paperCodes:
            self.baseQueryComponents.insert(0, '({formattedCodeString})')
            self.buildURLsforPaperCodes()

    def buildURLsforPaperCodes(self):
        paperSelectCQLStrings = CQLSelectStringForPapers(self.paperCodes).cqlSelectStrings
        self.queries = [
            self.baseQuery.format(formattedCodeString=codeString)
            for codeString in paperSelectCQLStrings
        ]
