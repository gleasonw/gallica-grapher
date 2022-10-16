from gallica.params import Params


class Ticket:

    def __init__(
            self,
            key,
            terms,
            codes,
            dateRange,
            linkTerm,
            linkDistance,
            searchType
    ):
        self.key = key
        self.params = Params(
            terms=terms,
            codes=codes,
            startDate=int(dateRange[0]),
            endDate=int(dateRange[1]),
            link=(linkTerm, linkDistance),
            grouping=searchType
        )

    def getID(self):
        return self.key

    def getTerms(self):
        return self.params.terms

    def getLinkTerm(self):
        return self.params.getLinkTerm()

    def getLinkDistance(self):
        return self.params.getLinkDistance()

    def getStartDate(self):
        return self.params.startDate

    def getEndDate(self):
        return self.params.endDate

    def getSearchType(self):
        return self.params.grouping

    def getCodes(self):
        return self.params.codes

    def getCodeBundles(self):
        return self.params.getCodeBundles()

    def getDateGroupings(self):
        return self.params.getDateGroupings()
