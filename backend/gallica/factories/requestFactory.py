from gallica.factories.parseFactory import buildParser
from gallica.searchprogresshandler import SearchProgressHandler
from gallica.papersearchrunner import PaperSearchRunner
from gallica.ticketsearchrunner import TicketSearchRunner
from gallica.factories.occurrenceQueryBuilder import OccurrenceQueryBuilder
from gallica.factories.paperQueryFactory import PaperQueryFactory
from dbops.schemaLinkForSearch import SchemaLinkForSearch
from gallica.concurrentfetch import ConcurrentFetch
from gallica.request import Request
from utils.psqlconn import PSQLconn


class RequestFactory:

    def __init__(self, tickets, requestid):
        self.dbConn = PSQLconn().getConn()
        self.requestID = requestid
        self.tickets = tickets
        self.occurrenceQueryBuilder = OccurrenceQueryBuilder()

    def build(self) -> Request:
        return Request(
            requestID=self.requestID,
            ticketSearches=list(map(self.buildTicketSearch, self.tickets)),
            dbConn=self.dbConn
        )

    def buildTicketSearch(self, ticket) -> SearchProgressHandler:
        self.occurrenceQueryBuilder.addQueriesAndNumResultsToTicket(ticket)
        return SearchProgressHandler(
            ticket=ticket,
            searchDriver=self.buildSearchRunner(ticket)
        )

    def buildSearchRunner(self, ticket) -> TicketSearchRunner:
        parse = buildParser()
        sruFetcher = ConcurrentFetch('https://gallica.bnf.fr/SRU')
        dbLink = SchemaLinkForSearch(
            requestID=self.requestID,
            conn=self.dbConn
        )
        paperSearch = PaperSearchRunner(
            parse=parse,
            paperQueryFactory=PaperQueryFactory(),
            sruFetch=sruFetcher,
            arkFetch=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
            insert=dbLink.insertRecordsIntoPapers
        )
        return TicketSearchRunner(
            parse=parse,
            ticket=ticket,
            requestID=self.requestID,
            schemaLink=dbLink,
            sruFetch=sruFetcher,
            paperAdd=paperSearch.addRecordDataForTheseCodesToDB,
        )


