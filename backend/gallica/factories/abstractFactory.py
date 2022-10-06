from gallica.factories.parseFactory import buildParser
from gallica.fullsearchprogressupdate import FullSearchProgressUpdate
from gallica.papersearchrunner import PaperSearchRunner
from gallica.factories.paperQueryFactory import PaperQueryFactory
from dbops.schemaLinkForSearch import SchemaLinkForSearch
from fetchComponents.concurrentfetch import ConcurrentFetch
from gallica.request import Request
from query import Query, PaperQuery
from query import CQLStringForPaperCodes
from utils.psqlconn import PSQLconn
from gallica.ticket import Ticket
from gallica.search import Search


NUM_CODES_PER_CQL = 10


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
        self.makeQuery = Query

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

    def buildAllSearchQueries(self, ticket) -> list:
        return list(map(
            self.makeQuery,
            cqlStrings
        ))

    def buildYearGroupQueries(self, ticket) -> list:


    def buildMonthGroupQueries(self, ticket) -> list:
        pass

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


