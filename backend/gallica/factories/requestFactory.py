from ticket import Ticket
from gallica.fulfillment import Fulfillment
from parse import Parse
from fulfillment import Fulfillment
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
            makeTicket=self.buildTicket,
            dbConn=self.dbConn
        )

    def buildTicket(self, queries, ticketID, progressThread) -> Ticket:
        search = self.buildOccurrenceFulfillment(
            queries,
            self.requestID,
            ticketID,
            self.dbConn
        )
        return Ticket(
            ticketID,
            self.requestID,
            search,
            progressThread
        )

    def buildOccurrenceFulfillment(self, options, requestID, ticketID, dbConnection) -> Fulfillment:
        parse = buildParser()
        fetcher = Fetch('https://gallica.bnf.fr/SRU')
        transaction = RecordsToDBTransaction(
            requestID=requestID,
            ticketID=ticketID,
            conn=dbConnection,
            getPaperRecordsForMissingCodes=None
        )
        return Fulfillment(
            parse=parse,
            urls=CQLFactory().buildStringsForOptions(options),
            makeQuery=Query,
            insertRecords=transaction.insertResults,
            fetcher=fetcher
        )

def buildParser() -> Parse:
    return Parse(
        PaperRecord,
        OccurrenceRecord,
        XMLParser(Date)
    )

