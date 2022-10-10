import threading
from gallica.factories.allSearchFactory import AllSearchFactory
from gallica.factories.groupSearchFactory import GroupSearchFactory
from gallica.ticketprogressstats import TicketProgressStats

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
            queryBuilder
    ):
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.state = 'RUNNING'
        self.requestID = requestID
        self.estimateNumRecords = 0
        self.DBconnection = dbConn
        self.ticketProgressStats = self.initProgressStats()
        self.tickets = tickets
        self.SRUapi = SRUapi
        self.dbLink = dbLink
        self.parse = parse
        self.queryBuilder = queryBuilder
        super().__init__()

    def setTicketSearches(self, ticketSearches):
        self.ticketSearches = ticketSearches

    def setRequestState(self, state):
        self.state = state
        print('Request state: ' + state)

    #TODO: too many ticket ids flying around
    def getProgressStats(self):
        return {
            ticket.getID(): self.ticketProgressStats[ticket.getID()].get()
            for ticket in self.tickets
        }

    def run(self):
        numRecords = sum([search.getNumRecords() for search in self.ticketSearches])
        if numRecords == 0:
            self.state = 'NO_RECORDS'
        else:
            if self.numRecordsUnderLimit(numRecords):
                self.doAllSearches()
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

    def doAllSearches(self):
        searchFactories = {
            'all': AllSearchFactory,
            'year': GroupSearchFactory,
            'month': GroupSearchFactory,
        }
        for ticket in self.tickets:
            self.state = 'RUNNING'
            search = searchFactories[ticket.fetchType](
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
                onAddingResultsToDB=lambda: self.setRequestState('ADDING_RESULTS_TO_DB'),
            ).getSearch()
            search.run()
        self.state = 'COMPLETED'

    def setTicketProgressStats(self, ticketKey, progressStats):
        self.ticketProgressStats[ticketKey].update(progressStats)

    def initProgressStats(self):
        progressDict = {
            ticket.getID(): TicketProgressStats(ticketID=ticket.getID())
            for ticket in self.tickets
        }
        return progressDict
