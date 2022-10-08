from gallica.factories.parseFactory import buildParser
from gallica.papersearchrunner import PaperSearchRunner
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
        self.sruFetcher = ConcurrentFetch('https://gallica.bnf.fr/SRU')
        self.paperSearch = PaperSearchRunner(
            parse=self.parse,
            paperQueryFactory=PaperSearchFactory(),
            sruFetch=self.sruFetcher,
            arkFetch=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
        )
        self.dbLink = SchemaLinkForSearch(
            requestID=self.requestID,
            paperFetcher=self.paperSearch.addRecordDataForTheseCodesToDB,
            conn=self.dbConn
        )
        self.baseQueries = QueryIndexer(gallicaAPI=self.sruFetcher)

    def buildRequest(self) -> Request:
        req = Request(
            requestID=self.requestID,
            dbConn=self.dbConn
        )
        ticketSearchBuilders = {
            'all': AllSearchFactory,
            'group': GroupSearchFactory
        }
        req.setTicketSearches(
            list(map(
                lambda tick: ticketSearchBuilders[tick.fetchType](
                    ticket=tick,
                    dbLink=self.dbLink,
                    parse=self.parse,
                    baseQueries=self.baseQueries,
                    requestID=self.requestID,
                    onUpdateProgress=lambda progressStats:
                        req.setTicketProgressStats(tick.getID(), progressStats),
                    onAddingResultsToDd=lambda: req.setRequestState('ADDING_RESULTS_TO_DB'),
                    sruFetcher=self.sruFetcher
                ).getSearch(),
                self.tickets
            ))
        )
        return req

