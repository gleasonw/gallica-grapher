from parseFactory import buildParser
from searchprogress import SearchProgress
from gallica.papersearch import PaperSearch
from ticketsearch import TicketSearch
from occurrenceQueryFactory import OccurrenceQueryFactory
from paperQueryFactory import PaperQueryFactory
from tableLink import TableLink
from fetch import Fetch
from request import Request
from utils.psqlconn import PSQLconn


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
        search = self.buildTicketSearch(queryData['queries'])
        return SearchProgress(
            ticketID=ticketID,
            searchDriver=search,
            estimateNumResults=queryData['estimateNumResults'],
            progressCallback=progressThread
        )

    def buildTicketSearch(self, queries) -> TicketSearch:
        parse = buildParser()
        sruFetcher = Fetch('https://gallica.bnf.fr/SRU')
        dbLink = TableLink(
            requestID=self.requestID,
            conn=self.dbConn
        )
        paperSearch = PaperSearch(
            parse=parse,
            paperQueryFactory=PaperQueryFactory(),
            sruFetch=sruFetcher,
            arkFetch=Fetch('https://gallica.bnf.fr/ark:/12148'),
            insert=dbLink.insertRecordsIntoPapers
        )
        return TicketSearch(
            parse=parse,
            queries=queries,
            schemaLink=dbLink,
            sruFetch=sruFetcher,
            paperAdd=paperSearch.addRecordDataForTheseCodesToDB,
        )


