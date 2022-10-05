from gallica.factories.parseFactory import buildParser
from gallica.fullsearchprogressupdate import FullSearchProgressUpdate
from gallica.papersearchrunner import PaperSearchRunner
from gallica.factories.fullOccurrenceQueryBuilder import FullOccurrenceQueryBuilder
from gallica.factories.paperQueryFactory import PaperQueryFactory
from dbops.schemaLinkForSearch import SchemaLinkForSearch
from fetchComponents.concurrentfetch import ConcurrentFetch
from gallica.request import Request
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
        queriesForFetch = {
            'year': lambda tick, _: self.buildYearGroupQueries(tick),
            'month': lambda tick, _: self.buildMonthGroupQueries(tick),
            'all': lambda tick, recordCount: self.buildAllSearchQueries(tick, recordCount)
        }
        if fetchType == 'all':
            progressHandler = FullSearchProgressUpdate(ticket, onProgressUpdate)
            insertSocket = dbLink.insertRecordsIntoOccurrences
            parseData = parse.parseOccurrences
            numRecords = self.allSearchEstimate(ticket)
        else:
            progressHandler = BasicProgressHandler(ticket, onProgressUpdate)
            insertSocket = dbLink.insertRecordsIntoGroupCounts
            parseData = parse.groupCounts
            numRecords = self.groupSearchEstimate(ticket)
        queries = queriesForFetch[fetchType](ticket, numRecords)
        return Search(
            ticketID=ticket.getID(),
            requestID=self.requestID,
            queries=queries,
            SRUfetch=sruFetcher,
            parseDataToRecords=parseData,
            insertRecordsIntoDatabase=insertSocket,
            onUpdateProgress=progressHandler.handleUpdateProgress,
            onSearchFinish=progressHandler.handleSearchFinish,
            getEstimateNumRecordsToFetch=getEstimateRecords
        )

    def buildAllSearchQueries(self, ticket, numRecords) -> Search:
        return FullOccurrenceQueryBuilder().addQueriesAndNumResultsToTicket(ticket)

    def buildYearGroupQueries(self, ticket) -> list:
        pass

    def buildMonthGroupQueries(self, ticket) -> list:
        pass

    def groupSearchEstimate(self, queries) -> int:
        pass

    def allSearchEstimate(self, queries) -> int:
        pass
