from cqlStringForPaperCodes import CQLStringForPaperCodes
from queryIndexer import QueryIndexer
from query import NumOccurrencesForTermQuery


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
        for term in self.ticket.terms:
            getThisTermCQL = self.cql.buildCQLforTerm(term)
            forTheseCodesCQL = self.cql.buildCQLforPaperCodes()
            for codesBunch in forTheseCodesCQL:
                combinedCQL = getThisTermCQL.format(formattedCodeString=codesBunch)
                yield self.makeBaseQuery(combinedCQL, term)

    def makeBaseQueriesOnlyTerms(self):
        for term in self.ticket.terms:
            cql = self.cql.buildCQLForTerm(term)
            yield self.makeBaseQuery(cql, term)


class CQLFactory:

    def __init__(self, ticket):
        self.ticket = ticket
        self.cqlForCodes = CQLStringForPaperCodes()

    def buildCQLforTerm(self, term) -> str:
        baseQueryComponents = []
        if self.ticket.startYear and self.ticket.endYear:
            baseQueryComponents.append(f'dc.date >= "{self.ticket.startYear}"')
            baseQueryComponents.append(f'dc.date <= "{self.ticket.endYear}"')
        baseQueryComponents.append(f'(gallica adj "{term}")')
        baseQueryComponents.append('(dc.type adj "fascicule")')
        if self.ticket.codes:
            baseQueryComponents.insert(0, '({formattedCodeString})')
        baseQuery = " and ".join(baseQueryComponents)
        baseQuery = f'{baseQuery} sortby dc.date/sort.ascending'
        return baseQuery

    def buildCQLforPaperCodes(self) -> list[str]:
        return self.cqlForCodes.build(self.ticket.codes)


