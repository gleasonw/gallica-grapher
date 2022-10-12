from dbops.schemaLinkForSearch import SchemaLinkForSearch
from gallica.fetchComponents.concurrentFetch import ConcurrentFetch
from gallica.request import Request
from utils.psqlconn import PSQLconn
from gallica.ticket import Ticket
from gallica.parse import Parse
from gallica.factories.ticketQueryFactory import TicketQueryFactory


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

        self.parse = Parse()
        self.dbConn = PSQLconn().getConn()
        self.SRUapi = ConcurrentFetch('https://gallica.bnf.fr/SRU')
        self.dbLink = SchemaLinkForSearch(
            requestID=self.requestID,
            tools=self
        )
        self.queryBuilder = TicketQueryFactory()

    def buildRequest(self) -> Request:
        return Request(
            requestID=self.requestID,
            dbConn=self.dbConn,
            tickets=self.tickets,
            SRUapi=self.SRUapi,
            dbLink=self.dbLink,
            parse=self.parse,
            queryBuilder=self.queryBuilder
        )
