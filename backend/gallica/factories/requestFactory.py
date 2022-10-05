from gallica.factories.parseFactory import buildParser
from gallica.fullsearchprogressupdate import FullSearchProgressUpdate
from gallica.papersearchrunner import PaperSearchRunner
from gallica.ticketsearchrunner import TicketSearchRunner
from gallica.factories.fullOccurrenceQueryBuilder import FullOccurrenceQueryBuilder
from gallica.factories.paperQueryFactory import PaperQueryFactory
from dbops.schemaLinkForSearch import SchemaLinkForSearch
from fetchComponents.concurrentfetch import ConcurrentFetch
from gallica.request import Request
from utils.psqlconn import PSQLconn
from gallica.ticket import Ticket
from gallica.search import Search


class RequestFactory:

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
                linkDistance=ticket.get('linkDistance')
            )
            for key, ticket in tickets.items()
        ]

    def build(self) -> Request:
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
        queriesForFetch = {
            'year': lambda x: self.buildYearGroupQueries(x),
            'month': lambda x: self.buildMonthGroupQueries(x),
            'all': lambda x: self.buildAllSearchQueries(x)
        }
        if fetchType == 'all':
            progressHandler = FullSearchProgressUpdate(ticket, onProgressUpdate)
            insertSocket = dbLink.insertRecordsIntoOccurrences
            parseData = parse.parseOccurrences
        else:
            progressHandler = BasicProgressHandler(ticket, onProgressUpdate)
            insertSocket = dbLink.insertRecordsIntoGroupCounts
            parseData = parse.groupCounts
        queries = queriesForFetch[fetchType](ticket)
        return Search(
            ticketID=ticket.getID(),
            requestID=self.requestID,
            queries=queries,
            SRUfetch=sruFetcher,
            parseDataToRecords=parseData,
            insertRecordsIntoDatabase=insertSocket,
            onUpdateProgress=progressHandler.handleUpdateProgress,
            onSearchFinish=progressHandler.handleSearchFinish
        )

    def buildAllSearchQueries(self, ticket) -> Search:
        return FullOccurrenceQueryBuilder().addQueriesAndNumResultsToTicket(ticket)

    def buildYearGroupQueries(self, ticket) -> list:
        pass

    def buildMonthGroupQueries(self, ticket) -> list:
        pass
