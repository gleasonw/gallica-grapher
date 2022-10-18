from query import OccurrenceQuery


class QueryBuilder:

    def __init__(self):
        pass

    def buildForBundle(self, bundle):
        if codes := bundle.getCodeBundles():
            return self.buildWithCodeBundles(bundle, codes)
        else:
            return self.buildNoCodeBundles(bundle)

    def buildWithCodeBundles(self, bundle, codeBundles):
        return [
            self.makeQuery(term, bundle, dates, codes)
            for term in bundle.getTerms()
            for dates in bundle.getDateGroupings()
            for codes in codeBundles
        ]

    def buildNoCodeBundles(self, bundle):
        return [
            self.makeQuery(term, dates, bundle)
            for term in bundle.getTerms()
            for dates in bundle.getDateGroupings()
        ]

    def makeQuery(self, term, dates, bundle, codes=None):
        raise NotImplementedError


class TicketQueryBuilder(QueryBuilder):
    def __init__(self):
        super().__init__()

    def buildQueriesForTicket(self, ticket):
        return self.buildForBundle(ticket)

    def makeQuery(self, term, ticket, dates, codes=None):
        codes = codes or []
        return OccurrenceQuery(
            term=term,
            ticket=ticket,
            startIndex=0,
            numRecords=1,
            collapsing=False,
            codes=codes,
            startDate=dates[0],
            endDate=dates[1]
        )


class ParamQueryBuilder(QueryBuilder):

    def __init__(self):
        super().__init__()

    def buildQueriesForParams(self, params):
        return self.buildForBundle(params)

    def makeQuery(self, term, params, dates, codes=None):
        codes = codes or []
        return OccurrenceQuery(
            term=term,
            ticket=params,
            startIndex=params.getStartIndex(),
            numRecords=params.getNumRecords(),
            collapsing=False,
            codes=codes,
            startDate=dates[0],
            endDate=dates[1]
        )

