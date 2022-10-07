from gallica.factories.parseFactory import buildParser
from gallica.papersearchrunner import PaperSearchRunner
from gallica.factories.paperQueryFactory import PaperQueryFactory
from dbops.schemaLinkForSearch import SchemaLinkForSearch
from fetchComponents.concurrentfetch import ConcurrentFetch
from gallica.request import Request
from query import Query, PaperQuery
from utils.psqlconn import PSQLconn
from gallica.ticket import Ticket
from gallica.search import Search


NUM_CODES_PER_CQL = 10


class AbstractFactory:

    def __init__(self, tickets, requestid):
        self.dbConn = PSQLconn().getConn()
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
        self.parse = buildParser()
        self.sruFetcher = ConcurrentFetch('https://gallica.bnf.fr/SRU')
        self.paperSearch = PaperSearchRunner(
            parse=self.parse,
            paperQueryFactory=PaperQueryFactory(),
            sruFetch=self.sruFetcher,
            arkFetch=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
        )
        self.dbLink = SchemaLinkForSearch(
            requestID=self.requestID,
            paperFetcher=self.paperSearch.addRecordDataForTheseCodesToDB,
            conn=self.dbConn
        )

    def buildRequest(self) -> Request:
        req = Request(
            requestID=self.requestID,
            dbConn=self.dbConn
        )
        req.setTicketSearches(
            list(map(
                lambda x: self.buildTicketSearch(x, req.setTicketProgressStats),
                self.tickets
            ))
        )
        return req

    def buildTicketSearch(self, ticket, onProgressUpdate) -> Search:
        fetchType = ticket.getFetchType()
        baseQueriesForSearch = {
            'year': lambda tick, _: self.buildYearGroupQueries(tick),
            'month': lambda tick, _: self.buildMonthGroupQueries(tick),
            'all': lambda tick, recordCount: self.buildAllSearchQueries(tick)
        }
        queries = baseQueriesForSearch[fetchType](ticket)
        progressHandler = self.buildProgressHandler(ticket, onProgressUpdate)
        if fetchType == 'all':
            insertSocket = self.dbLink.insertRecordsIntoOccurrences
            parseData = self.parse.occurrences
            numResultsForQueries = self.getNumResultsForEachQuery(queries)
            numRecords = sum(numResultsForQueries.values())
        else:
            insertSocket = self.dbLink.insertRecordsIntoGroupCounts
            parseData = self.parse.groupCounts
            numRecords = len(queries)
        return Search(
            ticketID=ticket.getID(),
            requestID=self.requestID,
            queries=queries,
            SRUfetch=self.sruFetcher,
            parseDataToRecords=parseData,
            insertRecordsIntoDatabase=insertSocket,
            onUpdateProgress=progressHandler.handleUpdateProgress,
            onSearchFinish=progressHandler.handleSearchFinish,
            numRecords=numRecords
        )

    def buildProgressHandler(self, ticket, onProgressUpdate):
        raise NotImplementedError

    def buildAllSearchQueries(self, ticket) -> list:
        return self.buildBaseQueries(
            ticket,
            [(ticket.getStartDate(), ticket.getEndDate())]

    def buildYearGroupQueries(self, ticket) -> list:
        return self.buildBaseQueries(
            ticket,
            set(zip(
                range(ticket.getStartDate(), ticket.getEndDate() + 1),
                range(ticket.getStartDate(), ticket.getEndDate() + 1)
            ))
        )
                
    def buildMonthGroupQueries(self, ticket) -> list:
        yearMonthDays = []
        for year in range(ticket.getStartDate(), ticket.getEndDate() + 1):
            for month in range(1, 13):
                yearMonthDays.append((f"{year}-{month:02}-01", f"{year}-{month:02}-31"))
        return self.buildBaseQueries(ticket, yearMonthDays)

    def makeQuery(self, data, codes=None):
        return Query(
            codes=codes,
            linkDistance=data.get('linkDistance'),
            linkTerm=data.get('linkTerm'),
            publicationStartDate=data.get('publicationStartDate'),
            publicationEndDate=data.get('publicationEndDate'),
            term=data.get('term'),
            numRecords=data.get('numRecords'),
            startIndex=data.get('startIndex'),
            collapsing=data.get('collapsing')
        )

    def buildBaseQueries(self, ticket, startEndDates):
        codeBundles = self.splitCodesIntoBundles(ticket.getCodes())
        for term in ticket.getTerms():
            for dates in startEndDates:
                queryData = {
                    "term":term,
                    "publicationStartDate":dates[0],
                    "publicationEndDate":dates[1],
                    "collapsing":False,
                    "numRecords":1,
                    "startIndex":0,
                }
                if codeBundles:
                    return [self.makeQuery(queryData, codes) for codes in codeBundles]
                else:
                    return [self.makeQuery(queryData)]

    def getNumResultsForEachQuery(self, queries) -> dict:
        responses = self.sruFetcher.fetchAll(queries)
        numResultsForQueries = {}
        for data, query in responses:
            numRecordsForBaseCQL = self.parse.numRecords(data)
            numResultsForQueries[query] = numRecordsForBaseCQL
        return numResultsForQueries

    def splitCodesIntoBundles(self, codes) -> list:
        return [
            codes[i:i+NUM_CODES_PER_CQL]
            for i in range(0, len(codes), NUM_CODES_PER_CQL)
        ]

    def makeIndexedQueries(self, baseQueries):
        for query in baseQueries.values():
            for index in range(1, query.estimateNumRecordsToFetch, 50):
                yield Query(
                    cql=query.cql,
                    startIndex=index,
                    numRecords=50,
                    collapsing=False,
                    term=query.term
                )

    def makeIndexedPaperQueries(self, baseQueries, totalResults):
        queries = []
        for cql in baseQueries:
            for index in range(1, totalResults, 50):
                queries.append(
                    PaperQuery(
                        cql=cql,
                        startIndex=index
                    )
                )
        return queries


