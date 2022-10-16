from dbops.schemaLinkForSearch import SchemaLinkForSearch
from concurrentFetch import ConcurrentFetch
from gallica.request import Request
from utils.psqlconn import PSQLconn
from gallica.ticket import Ticket
from gallicaxmlparse import GallicaXMLparse
from queryBuilder import TicketQueryFactory


class RequestFactory:

    def __init__(self, tickets, requestid):
        self.requestID = requestid
        self.tickets = [
            Ticket(
                key=key,
                terms=ticket['terms'],
                codes=ticket['codes'],
                dateRange=[
                    ticket['startYear'],
                    ticket['endYear']
                ],
                linkTerm=ticket.get('linkTerm'),
                linkDistance=ticket.get('linkDistance'),
                searchType=ticket['searchType']
            )
            for key, ticket in tickets.items()
        ]

        self.parse = GallicaXMLparse()
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
