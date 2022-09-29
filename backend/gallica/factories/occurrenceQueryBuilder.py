from gallica.factories.cqlStringForPaperCodes import CQLStringForPaperCodes
from gallica.factories.queryIndexer import QueryIndexer
from fetchComponents.query import NumOccurrencesForTermQuery


class OccurrenceQueryBuilder:

    def __init__(self):
        self.cql = None
        self.ticket = None
        self.makeIndexer = lambda queries: QueryIndexer(queries)
        self.makeCQLFactory = lambda ticket: CQLFactory(ticket)
        self.makeBaseQuery = lambda cql, term: NumOccurrencesForTermQuery(cql, term)

    def addQueriesAndNumResultsToTicket(self, ticket):
        self.ticket = ticket
        self.cql = self.makeCQLFactory(ticket)
        if self.ticket.codes:
            queries = self.makeBaseQueriesForTermsAndCodes()
        else:
            queries = self.makeBaseQueriesOnlyTerms()
        indexer = self.makeIndexer(queries)
        numResultsForTicket = indexer.fetchNumResultsForQueries()
        indexedQueries = indexer.makeIndexedQueries()
        self.ticket.setQueries(indexedQueries)
        self.ticket.setEstimateNumResults(numResultsForTicket)

    def makeBaseQueriesForTermsAndCodes(self):
        baseQueries = []
        for term in self.ticket.terms:
            getThisTermCQL = self.cql.buildCQLforTerm(term)
            forTheseCodesCQL = self.cql.buildCQLforPaperCodes()
            for codesBunch in forTheseCodesCQL:
                combinedCQL = getThisTermCQL.format(formattedCodeString=codesBunch)
                baseQueries.append(self.makeBaseQuery(combinedCQL, term))
        return baseQueries

    def makeBaseQueriesOnlyTerms(self):
        baseQueries = []
        for term in self.ticket.terms:
            cql = self.cql.buildCQLforTerm(term)
            baseQueries.append(self.makeBaseQuery(cql, term))
        return baseQueries


class CQLFactory:

    def __init__(self, ticket):
        self.ticket = ticket
        self.cqlForCodes = CQLStringForPaperCodes()

    def buildCQLforTerm(self, term) -> str:
        codeSelect = '({formattedCodeString}) and '
        startYearSelect = f'dc.date >= "{self.ticket.startYear}" and '
        endYearSelect = f'dc.date <= "{self.ticket.endYear}" and '
        simpleSearchSelect = f'(gallica adj "{term}") and '
        linkSearchSelect = f'(text adj "{term}" prox/unit=word/distance={self.ticket.linkDistance} "{self.ticket.linkTerm}") and '
        query = (
            f"{codeSelect if self.ticket.codes else ''}"
            f"{startYearSelect if self.ticket.startYear else ''}"
            f"{endYearSelect if self.ticket.endYear else ''}"
            f"{simpleSearchSelect if self.ticket.linkTerm is None else linkSearchSelect}"
            '(dc.type all "fascicule")'
        )
        return query

    def buildCQLforPaperCodes(self) -> list:
        return self.cqlForCodes.build(self.ticket.codes)
