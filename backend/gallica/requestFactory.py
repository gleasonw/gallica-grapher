from ticket import Ticket
from gallica.search import Search
from parse import Parse
from search import PaperSearchFulfillment
from search import OccurrenceSearchFulfillment
from dto.paperRecord import PaperRecord
from dto.occurrenceRecord import OccurrenceRecord
from xmlParser import XMLParser
from date import Date
from dto.query import Query
from cqlforticket import CQLforTicket
from recordsToDBTransaction import RecordsToDBTransaction
from fetch import Fetch
from request import Request
from utils.psqlconn import PSQLconn


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
        driver = Search()
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

    def buildOccurrenceFulfillment(self, options, requestID, ticketID, dbConnection) -> OccurrenceSearchFulfillment:
        parse = self.buildParser()
        fetcher = Fetch('https://gallica.bnf.fr/SRU')
        transaction = RecordsToDBTransaction(
            requestID=requestID,
            ticketID=ticketID,
            conn=dbConnection,
            getPaperRecordsForMissingCodes=None
        )
        return OccurrenceSearchFulfillment(
            parse=parse,
            urls=CQLforTicket().buildCQLstrings(options),
            makeQuery=Query,
            insertRecords=transaction.insertResults,
            fetcher=fetcher
        )

    def buildPaperFulfillment(self) -> PaperSearchFulfillment:
        pass

    def buildParser(self) -> Parse:
        return Parse(
            PaperSearchFulfillment,
            OccurrenceSearchFulfillment,
            PaperRecord,
            OccurrenceRecord,
            XMLParser(Date)
        )

