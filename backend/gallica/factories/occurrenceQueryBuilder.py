from cqlStringForPaperCodes import CQLStringForPaperCodes
from queryIndexer import QueryIndexer
from batchedQueries import BatchedQueries


class OccurrenceQueryBuilder:

    def __init__(self):
        self.cql = None
        self.ticket = None
        self.indexer = None
        self.queryBatcher = BatchedQueries(batchSize=200).batchQueries

    def addQueriesAndNumResultsToTicket(self, ticket):
        self.ticket = ticket
        self.indexer = QueryIndexer()
        self.cql = CQLFactory(ticket)
        if self.ticket.codes:
            cql = self.makeCQLForTermsAndCodes()
        else:
            cql = self.makeCQLOnlyTerms()
        indexedQueries = self.indexer.makeQueriesIndexedOnNumResultsForBaseCQL(cql)
        batchedQueries = self.queryBatcher(indexedQueries)
        self.ticket.setQueries(batchedQueries)
        self.ticket.setEstimateNumResults(self.indexer.totalResultsForTicket)

    def makeCQLForTermsAndCodes(self):
        for term in self.ticket.terms:
            getThisTermCQL = self.cql.buildCQLForTerm(term)
            forTheseCodesCQL = self.cql.buildCQLForPaperCodes()
            for codesBunch in forTheseCodesCQL:
                combinedCQL = getThisTermCQL.format(formattedCodeString=codesBunch)
                yield combinedCQL

    def makeCQLOnlyTerms(self):
        for term in self.ticket.terms:
            yield self.cql.buildCQLForTerm(term)


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


