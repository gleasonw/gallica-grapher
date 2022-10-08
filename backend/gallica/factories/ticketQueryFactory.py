from fetchComponents.query import Query


class TicketQueryFactory:

    def __init__(self, queryOps):
        self.queryOps = queryOps

    def build(self, ticket, startEndDates):
        for term in ticket.getTerms():
            for dates in startEndDates:
                if codeBundles := ticket.getCodeBundles():
                    return [
                        self.makeQuery(
                            term=term,
                            ticket=ticket,
                            dates=dates,
                            codes=codes
                        )
                        for codes in codeBundles
                    ]
                else:
                    return [
                        self.makeQuery(
                            term=term,
                            ticket=ticket,
                            dates=dates
                        )
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
