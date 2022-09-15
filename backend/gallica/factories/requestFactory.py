from parseFactory import buildParser
from searchprogresshandler import SearchProgressHandler
from gallica.papersearchrunner import PaperSearchRunner
from ticketsearchrunner import TicketSearchRunner
from occurrenceQueryBuilder import OccurrenceQueryBuilder
from paperQueryFactory import PaperQueryFactory
from tableLink import TableLink
from fetch import Fetch
from request import Request
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
            ticketSearches=map(self.buildTicketSearch, self.tickets),
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
        sruFetcher = Fetch('https://gallica.bnf.fr/SRU')
        dbLink = TableLink(
            requestID=self.requestID,
            conn=self.dbConn
        )
        paperSearch = PaperSearchRunner(
            parse=parse,
            paperQueryFactory=PaperQueryFactory(),
            sruFetch=sruFetcher,
            arkFetch=Fetch('https://gallica.bnf.fr/ark:/12148'),
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


