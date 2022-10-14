import threading
from gallica.factories.allSearchFactory import AllSearchFactory
from gallica.factories.groupSearchFactory import GroupSearchFactory
from gallica.searchprogressstats import SearchProgressStats

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000


class Request(threading.Thread):
    def __init__(
            self,
            requestID,
            dbConn,
            tickets,
            SRUapi,
            dbLink,
            parse,
            queryBuilder,
    ):
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.state = 'RUNNING'
        self.requestID = requestID
        self.estimateNumRecords = 0
        self.DBconnection = dbConn
        self.tickets = tickets
        self.SRUapi = SRUapi
        self.dbLink = dbLink
        self.parse = parse
        self.queryBuilder = queryBuilder
        self.searches = None
        self.ticketProgressStats = self.initProgressStats()
        super().__init__()

    #TODO: too many ticket ids flying around
    def getProgressStats(self):
        return {
            ticket.getID(): self.ticketProgressStats[ticket.getID()].get()
            for ticket in self.tickets
        }

    def setRequestState(self, state):
        self.state = state

    def run(self):
        self.searches = self.buildSearchesForTickets()
        self.setRecordsToFetchForProgressStats()
        numRecords = sum([
            search.getNumRecordsToBeInserted()
            for search in self.searches
        ])
        if numRecords == 0:
            self.state = 'NO_RECORDS'
        else:
            if self.numRecordsUnderLimit(numRecords):
                self.doEachSearch()
            else:
                self.state = 'TOO_MANY_RECORDS'
        self.DBconnection.close()

    def numRecordsUnderLimit(self, numRecords):
        dbSpaceRemainingWithBuffer = MAX_DB_SIZE - self.getNumberRowsStoredInAllTables() - 10000
        return numRecords < min(dbSpaceRemainingWithBuffer, RECORD_LIMIT)

    def getNumberRowsStoredInAllTables(self):
        with self.DBconnection.cursor() as curs:
            curs.execute(
                """
                SELECT sum(reltuples)::bigint AS estimate
                FROM pg_class
                WHERE relname IN ('results', 'papers');
                """
            )
            return curs.fetchone()[0]

    def buildSearchesForTickets(self):
        searchFactories = {
            'all': AllSearchFactory,
            'year': GroupSearchFactory,
            'month': GroupSearchFactory,
        }
        return [
            searchFactories[ticket.searchType](
                ticket=ticket,
                dbLink=self.dbLink,
                requestID=self.requestID,
                parse=self.parse,
                sruFetcher=self.SRUapi,
                queryBuilder=self.queryBuilder,
                onUpdateProgress=lambda progressStats: self.setTicketProgressStats(
                    ticket.getID(),
                    progressStats
                ),
                onAddingResultsToDB=lambda: self.setRequestState('ADDING_RESULTS'),
            ).prepare(self)
            for ticket in self.tickets
        ]

    def doEachSearch(self):
        for search in self.searches:
            self.state = 'RUNNING'
            search.run()
            self.ticketProgressStats[search.getTicketID()].setComplete()
        self.state = 'COMPLETED'

    def setTicketProgressStats(self, ticketID, progressStats):
        self.ticketProgressStats[ticketID].update(progressStats)

    def initProgressStats(self):
        progressDict = {
            ticket.getID(): SearchProgressStats(
                ticketID=ticket.getID(),
                searchType=ticket.getSearchType(),
                parse=self.parse
            )
            for ticket in self.tickets
        }
        return progressDict

    def setRecordsToFetchForProgressStats(self):
        for search in self.searches:
            self.ticketProgressStats[search.getTicketID()].setNumRecordsToFetch(
                search.getNumRecordsToBeInserted()
            )
