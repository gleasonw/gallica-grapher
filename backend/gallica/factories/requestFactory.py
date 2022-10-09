from gallica.factories.parseFactory import buildParser
from gallica.factories.paperSearchFactory import PaperSearchFactory
from dbops.schemaLinkForSearch import SchemaLinkForSearch
from fetchComponents.concurrentfetch import ConcurrentFetch
from gallica.request import Request
from utils.psqlconn import PSQLconn
from gallica.ticket import Ticket
from gallica.progressupdate import ProgressUpdate
from factories.allSearchFactory import AllSearchFactory
from factories.groupSearchFactory import GroupSearchFactory
from factories.queryIndexer import QueryIndexer
from factories.paperQuery


class RequestFactory:

    def __init__(self, tickets, requestid):
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

        self.dbConn = PSQLconn().getConn()
        self.parse = buildParser()
        self.SRUapi = ConcurrentFetch('https://gallica.bnf.fr/SRU')
        self.dbLink = SchemaLinkForSearch(
            requestID=self.requestID,
            tools=self
        )

    def buildRequest(self) -> Request:
        req = Request(
            requestID=self.requestID,
            dbConn=self.dbConn,
            tickets=self.tickets,
            SRUapi=self.SRUapi,
            dbLink=self.dbLink
        )
        return req

