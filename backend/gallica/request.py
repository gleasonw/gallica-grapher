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

    def setTicketSearches(self, ticketSearches):
        self.ticketSearches = ticketSearches

    def setRequestState(self, state):
        self.state = state
        print('Request state: ' + state)

    def getProgressStats(self):
        return self.ticketProgressStats

    def run(self):
        numRecords = self.getNumRecords()
        if self.numRecordsUnderLimit(numRecords):
            if numRecords:
                self.doAllSearches()
            else:
                self.state = 'NO_RECORDS'
        else:
            self.state = 'TOO_MANY_RECORDS'
        self.DBconnection.close()

    def getNumRecords(self):
        return sum([search.getNumRecords() for search in self.ticketSearches])

    def numRecordsUnderLimit(self, numRecords):
        dbSpaceRemainingWithBuffer = MAX_DB_SIZE - self.getNumberRowsStoredInAllTables() - 10000
        return numRecords < min(dbSpaceRemainingWithBuffer, RECORD_LIMIT)

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
            search.setProgressCallback(self.setTicketProgressStats)
            self.setTicketActive(search)
            search.initSearch(
                onAddMissingPapers=lambda: self.setRequestState('ADDING_MISSING_PAPERS'),
                onAddResults=lambda: self.setRequestState('ADDING_RESULTS'),
                onRemoveDuplicates=lambda: self.setRequestState('REMOVING_DUPLICATES')
            )
            self.setTicketProgressTo100AndMarkAsDone(search)
        self.state = 'COMPLETED'

    def setTicketActive(self, search):
        ticketID = search.getTicketID()
        self.ticketProgressStats[ticketID]['active'] = 1

    def setTicketProgressStats(self, ticketKey, progressStats):
        self.ticketProgressStats[ticketKey] = progressStats

    def setTicketProgressTo100AndMarkAsDone(self, search):
        numRetrieved = search.getNumRetrievedForTicket()
        ticketID = search.getTicketID()
        self.setTicketProgressStats(ticketID, {
            'progress': 100,
            'numResultsDiscovered': numRetrieved,
            'numResultsRetrieved': numRetrieved,
            'randomPaper': None,
            'estimateSecondsToCompletion': 0,
            'active': 0
        })

