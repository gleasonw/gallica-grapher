from searchprogress import SearchProgress
from gallica.papersearch import PaperSearch
from parse import Parse
from ticketsearch import TicketSearch
from dto.paperRecord import PaperRecord
from dto.occurrenceRecord import OccurrenceRecord
from xmlParser import XMLParser
from date import Date
from query import Query
from occurrenceQueryFactory import OccurrenceQueryFactory
from tableLink import TableLink
from fetch import Fetch
from request import Request
from utils.psqlconn import PSQLconn
from batchedQueries import BatchedQueries


#TODO: pass queries to ticket, not options
class RequestFactory:

    def __init__(self):
        self.dbConn = None
        self.requestID = None
        self.occurrenceQueryFactory = OccurrenceQueryFactory()

    def buildRequest(self, keyedOptions, requestid) -> Request:
        self.dbConn = PSQLconn().getConn()
        self.requestID = requestid
        queries = {}
        for key, options in keyedOptions:
            queries[key] = self.occurrenceQueryFactory.buildQueriesForOptions(options)
        return Request(
            queries=queries,
            requestID=requestid,
            makeTicket=self.buildTicketProgressHandler,
            dbConn=self.dbConn
        )

    def buildTicketProgressHandler(self, queryData, ticketID, progressThread) -> SearchProgress:
        search = buildTicketSearch(
            queryData['queries'],
            self.requestID,
            self.dbConn
        )
        return SearchProgress(
            ticketID=ticketID,
            searchDriver=search,
            estimateNumResults=queryData['estimateNumResults'],
            progressCallback=progressThread
        )


def buildTicketSearch(queries, requestID, dbConnection) -> TicketSearch:
    parse = buildParser()
    sruFetcher = Fetch('https://gallica.bnf.fr/SRU')
    dbLink = TableLink(
        requestID=requestID,
        conn=dbConnection
    )
    paperSearch = PaperSearch(
        parse=parse,
        paperQueryFactory=Query,
        sruFetch=sruFetcher,
        arkFetch=Fetch('https://gallica.bnf.fr/ark:/12148'),
        insert=dbLink.insert
    )
    return TicketSearch(
        parse=parse,
        queries=queries,
        schemaLink=dbLink,
        sruFetch=sruFetcher,
        paperAdd=paperSearch.addRecordDataForTheseCodesToDB
    )


def buildParser() -> Parse:
    return Parse(
        makePaperRecord=PaperRecord,
        makeOccurrenceRecord=OccurrenceRecord,
        xmlParser=XMLParser(Date)
    )

