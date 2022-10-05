from gallica.factories.parseFactory import buildParser
from gallica.fullsearchprogressupdate import FullSearchProgressUpdate
from gallica.papersearchrunner import PaperSearchRunner
from gallica.factories.fullOccurrenceQueryBuilder import FullOccurrenceQueryBuilder
from gallica.factories.paperQueryFactory import PaperQueryFactory
from dbops.schemaLinkForSearch import SchemaLinkForSearch
from fetchComponents.concurrentfetch import ConcurrentFetch
from gallica.request import Request
from query import Query, PaperQuery
from utils.psqlconn import PSQLconn
from gallica.ticket import Ticket
from gallica.search import Search


class AbstractFactory:

    def __init__(self, tickets, requestid):
        self.dbConn = PSQLconn().getConn()
        self.requestID = requestid
        self.tickets = [
            Ticket(
                key=key,
                terms=ticket['terms'],
                codes=ticket['codes'],
                dateRange=ticket['dateRange'],
                linkTerm=ticket.get('linkTerm'),
                linkDistance=ticket.get('linkDistance'),
                fetchType=ticket['fetchType']
            )
            for key, ticket in tickets.items()
        ]
        self.paperCqlBuilder = CQLStringForPaperCodes().build

    def buildRequest(self) -> Request:
        req = Request(
            requestID=self.requestID,
            dbConn=self.dbConn
        )
        req.setTicketSearches(
            list(map(
                lambda x: self.buildTicketSearch(x, req.setTicketProgressStats),
                self.tickets
            ))
        )

    def buildTicketSearch(self, ticket, onProgressUpdate) -> Search:
        parse = buildParser()
        sruFetcher = ConcurrentFetch('https://gallica.bnf.fr/SRU')
        paperSearch = PaperSearchRunner(
            parse=parse,
            paperQueryFactory=PaperQueryFactory(),
            sruFetch=sruFetcher,
            arkFetch=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
        )
        dbLink = SchemaLinkForSearch(
            requestID=self.requestID,
            paperFetcher=paperSearch.addRecordDataForTheseCodesToDB,
            conn=self.dbConn
        )
        return self.buildSearch(
            parse=parse,
            ticket=ticket,
            sruFetcher=sruFetcher,
            dbLink=dbLink,
            onProgressUpdate=onProgressUpdate
        )

    def buildSearch(self, parse, ticket, sruFetcher, dbLink, onProgressUpdate) -> Search:
        ticket = ticket
        fetchType = ticket.fetchType
        baseQueriesForFetch = {
            'year': lambda tick, _: self.buildYearGroupQueries(tick),
            'month': lambda tick, _: self.buildMonthGroupQueries(tick),
            'all': lambda tick, recordCount: self.buildAllSearchQueries(tick, recordCount)
        }
        queries = baseQueriesForFetch[fetchType](ticket)
        if fetchType == 'all':
            progressHandler = FullSearchProgressUpdate(ticket, onProgressUpdate)
            insertSocket = dbLink.insertRecordsIntoOccurrences
            parseData = parse.parseOccurrences
            numRecords = self.allSearchEstimate(queries)
        else:
            progressHandler = BasicProgressHandler(ticket, onProgressUpdate)
            insertSocket = dbLink.insertRecordsIntoGroupCounts
            parseData = parse.groupCounts
            numRecords = self.groupSearchEstimate(queries)
        return Search(
            ticketID=ticket.getID(),
            requestID=self.requestID,
            queries=queries,
            SRUfetch=sruFetcher,
            parseDataToRecords=parseData,
            insertRecordsIntoDatabase=insertSocket,
            onUpdateProgress=progressHandler.handleUpdateProgress,
            onSearchFinish=progressHandler.handleSearchFinish,
            numRecords=numRecords
        )

    def buildAllSearchQueries(self, ticket) -> Search:
        if ticket.getPaperCodes():



    def buildYearGroupQueries(self, ticket) -> list:
        pass

    def buildMonthGroupQueries(self, ticket) -> list:
        pass

    def groupSearchEstimate(self, queries) -> int:
        pass

    def allSearchEstimate(self, queries) -> int:
        responses = fetch.fetchAll(baseQueries.values())
        totalResults = 0
        for data, cql in responses:
            numRecordsForBaseCQL = parse.numRecords(data)
            totalResults += numRecordsForBaseCQL
            baseQueries[cql].estimateNumRecordsToFetch = numRecordsForBaseCQL
        return totalResults

    def indexAllSearchQueries(self, ticket):
        self.ticket = ticket
        self.cql = self.makeCQLFactory(ticket)
        if self.ticket.codes:
            queries = self.makeBaseQueriesForTermsAndCodes()
        else:
            queries = self.makeBaseQueriesOnlyTerms()
        indexer = self.makeIndexer(queries)
        numResultsForTicket = fetchNumResultsForQueries(indexer.fetch, indexer.baseQueries, indexer.parse)
        indexedQueries = makeIndexedQueries(indexer.baseQueries)
        self.ticket.setQueries(indexedQueries)
        self.ticket.setEstimateNumResults(numResultsForTicket)

    def fetchNumResultsForQueries(self, fetch, baseQueries, parse):
        responses = fetch.fetchAll(baseQueries.values())
        totalResults = 0
        for data, cql in responses:
            numRecordsForBaseCQL = parse.numRecords(data)
            totalResults += numRecordsForBaseCQL
            baseQueries[cql].estimateNumRecordsToFetch = numRecordsForBaseCQL
        return totalResults

    def makeIndexedQueries(self, baseQueries):
        for query in baseQueries.values():
            for index in range(1, query.estimateNumRecordsToFetch, 50):
                yield Query(
                    cql=query.cql,
                    startIndex=index,
                    numRecords=50,
                    collapsing=False,
                    term=query.term
            )

    def makeIndexedPaperQueries(self, baseQueries, totalResults):
        queries = []
        for cql in baseQueries:
            for index in range(1, totalResults, 50):
                queries.append(
                    PaperQuery(
                        cql=cql,
                        startIndex=index
                    )
                )
        return queries

    def makeBaseQueriesForTermsAndCodes(self):
        baseQueries = []
        for term in self.ticket.terms:
            getThisTermCQL = self.cql.buildTermCQL(term)
            forTheseCodesCQL = self.cql.buildCQLforPaperCodes()
            for codesBunch in forTheseCodesCQL:
                combinedCQL = getThisTermCQL.format(formattedCodeString=codesBunch)
                baseQueries.append(self.makeBaseQuery(combinedCQL, term))
        return baseQueries

    def makeBaseQueriesOnlyTerms(self):
        baseQueries = []
        for term in self.ticket.terms:
            cql = self.cql.buildTermCQL(term)
            baseQueries.append(self.makeBaseQuery(cql, term))
        return baseQueries

    def buildCQL(self, ticket):
        paperCodeCQL = self.buildCQLforPaperCodes(ticket.getPaperCodes())
        cqlStrings = []
        for term in ticket.getTerms():
            termCQL = self.buildTermCQL(term)
            cqlWithDateSelect = self.buildDateCQL(ticket)
            if paperCodeCQL:
                for codeBatchCQL in paperCodeCQL:
                    for dateSelect in cqlWithDateSelect:
                        cqlStrings.append(f"{termCQL} {dateSelect} {codeBatchCQL}")
                    cqlStrings.append(cqlWithDateSelect.format(formattedCodeString=codeBatchCQL))
            else:
                cqlStrings.append(f"{termCQL} {cqlWithDateSelect}")

    def buildTermCQL(self, term) -> str:
        simpleSearchSelect = f'(gallica adj "{term}")'
        linkSearchSelect = f'(text adj "{term}" prox/unit=word/distance={self.ticket.linkDistance} "{self.ticket.linkTerm}")'
        return f"{simpleSearchSelect if not self.ticket.linkTerm else linkSearchSelect}"

    def buildDateCQL(self, ticket) -> str:
        pass

    def buildCQLforPaperCodes(self, codes) -> list:
        return self.paperCqlBuilder(codes)


NUM_CODES_PER_CQL = 10


class CQLStringForPaperCodes:
    def __init__(self, numCodesPerCQL=NUM_CODES_PER_CQL):
        self.numCodesPerCQL = numCodesPerCQL

    def build(self, codes):
        cqlStrings = []
        for i in range(0, len(codes), self.numCodesPerCQL):
            codeChunks = codes[i:i + self.numCodesPerCQL]
            formattedCodes = [f"{code}_date" for code in codeChunks]
            CQLpaperSelectString = 'arkPress adj "' + '" or arkPress adj "'.join(
                formattedCodes) + '"'
            cqlStrings.append(CQLpaperSelectString)
        return cqlStrings
