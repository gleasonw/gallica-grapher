from ticket import Ticket
from gallica.fulfillment import BatchedSearch
from parse import Parse
from fulfillment import PaperSearchFulfillment
from fulfillment import Fulfillment
from dto.paperRecord import PaperRecord
from dto.occurrenceRecord import OccurrenceRecord
from xmlParser import XMLParser
from date import Date
from dto.query import Query
from cqlFactory import CQLFactory
from tableLink import RecordsToDBTransaction
from fetch import Fetch
from request import Request
from utils.psqlconn import PSQLconn

#TODO: make queries here based on options
class RequestFactory:

    def __init__(self):
        self.dbConn = None
        self.requestID = None

    def buildRequest(self, keyedOptions, requestid) -> Request:
        self.dbConn = PSQLconn().getConn()
        self.requestID = requestid
        return Request(
            tickets=keyedOptions,
            requestID=requestid,
            makeTicket=self.buildTicket,
            dbConn=self.dbConn
        )

    def buildTicket(self, options, ticketID, progressThread) -> Ticket:
        driver = BatchedSearch()
        fulfiller = self.buildOccurrenceFulfillment(
            options,
            self.requestID,
            ticketID,
            self.dbConn
        )
        return Ticket(
            ticketID,
            self.requestID,
            driver,
            fulfiller,
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
            urls=CQLFactory().buildCQLstrings(options),
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

