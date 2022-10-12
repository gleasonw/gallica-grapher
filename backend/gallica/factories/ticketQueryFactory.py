from query import Query


class TicketQueryFactory:
    def __init__(self):
        pass

    def build(self, ticket):
        if codes := ticket.getCodeBundles():
            return self.buildWithCodeBundles(ticket, codes)
        else:
            return self.buildNoCodeBundles(ticket)

    def buildWithCodeBundles(self, ticket, codeBundles):
        return [
            self.makeQuery(term, ticket, dates, codes)
            for term in ticket.getTerms()
            for dates in ticket.getDateGroupings()
            for codes in codeBundles
        ]

    def buildNoCodeBundles(self, ticket):
        return [
            self.makeQuery(term, ticket, dates)
            for term in ticket.getTerms()
            for dates in ticket.getDateGroupings()
        ]

    def makeQuery(self, term, ticket, dates, codes=None):
        codes = codes or []
        return Query(
            term=term,
            publicationStartDate=dates[0],
            publicationEndDate=dates[1],
            linkTerm=ticket.getLinkTerm(),
            linkDistance=ticket.getLinkDistance(),
            startIndex=0,
            numRecords=1,
            collapsing=False,
            codes=codes
        )
