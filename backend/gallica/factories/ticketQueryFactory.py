from gallica.fetchComponents.query import TicketQuery


class TicketQueryFactory:
    def __init__(self):
        pass

    def buildForTicket(self, ticket):
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
        return TicketQuery(
            term=term,
            ticket=ticket,
            startIndex=0,
            numRecords=1,
            collapsing=False,
            codes=codes,
            startDate=dates[0],
            endDate=dates[1]
        )
