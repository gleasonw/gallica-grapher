from ticketprogresshandler import TicketProgressHandler
from gallica.search import Search
from parse import Parse
from search import Search
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

    def buildTicketProgressHandler(self, queries, ticketID, progressThread) -> TicketProgressHandler:
        search = buildTicketSearch(
            queries,
            self.requestID,
            self.dbConn
        )
        return TicketProgressHandler(
            ticketID,
            search,
            progressThread
        )


def buildTicketSearch(queries, requestID, dbConnection) -> Search:
    parse = buildParser()
    fetcher = Fetch('https://gallica.bnf.fr/SRU')
    dbLink = TableLink(
        requestID=requestID,
        conn=dbConnection
    )
    return Search(
        parse=parse,
        queries=BatchedQueries(queries, 200).batchedQueries,
        insertRecords=dbLink.insert,
        fetcher=fetcher
    )


def buildParser() -> Parse:
    return Parse(
        PaperRecord,
        OccurrenceRecord,
        XMLParser(Date)
    )

