import threading

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000


class Request(threading.Thread):
    def __init__(self, requestID, dbConn):
        self.ticketSearches = None
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.state = 'RUNNING'
        self.requestID = requestID
        self.estimateNumRecords = 0
        self.DBconnection = dbConn
        self.ticketProgressStats = self.initProgressStats()
        super().__init__()

    def initProgressStats(self):
        progressDict = {}
        for index, search in enumerate(self.ticketSearches):
            key = search.getTicketID()
            progressDict[key] = {
                'progress': 0,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 0,
                'randomPaper': None,
                'estimateSecondsToCompletion': 0,
                'active': 1 if index == 0 else 0
            }
        return progressDict

    def setTicketSearches(self, ticketSearches):
        self.ticketSearches = ticketSearches

    def setRequestState(self, state):
        self.state = state
        print('Request state: ' + state)

    def getProgressStats(self):
        return self.ticketProgressStats

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
        for search in self.ticketSearches:
            self.state = 'RUNNING'
            search.run()
        self.state = 'COMPLETED'

    def setTicketProgressStats(self, ticketKey, progressStats):
        self.ticketProgressStats[ticketKey] = progressStats
