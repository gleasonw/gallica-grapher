import threading

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000


class Request(threading.Thread):
    def __init__(self, requestID, ticketSearches, dbConn):
        self.ticketSearches = ticketSearches
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.state = 'running'
        self.requestID = requestID
        self.estimateNumRecords = 0
        self.DBconnection = dbConn
        self.ticketProgressStats = self.initProgressStats()
        super().__init__()

    def setRequestState(self, state):
        self.state = state
        print('Request state: ' + state)

    def getProgressStats(self):
        return self.ticketProgressStats

    def run(self):
        self.estimateNumRecords = sum(
            [
                tick.getEstimateNumResultsForTicket()
                for tick in self.ticketSearches
            ]
        )
        if self.estimateNumRecords == 0:
            self.state = 'noRecords'
        elif self.numResultsOverLimit():
            self.state = 'tooManyRecords'
        else:
            self.doAllSearches()
        self.DBconnection.close()

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

    def numResultsOverLimit(self):
        dbSpaceRemainingWithBuffer = MAX_DB_SIZE - self.getNumberRowsStoredInAllTables() - 10000
        return self.estimateNumRecords > min(dbSpaceRemainingWithBuffer, RECORD_LIMIT)

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
        for progressHandler in self.ticketSearches:
            progressHandler.setProgressCallback(self.setTicketProgressStats)
            self.setTicketActive(progressHandler)
            progressHandler.initSearch({
                'onAddMissingPapers': lambda: self.setRequestState('addingMissingPapers'),
                'onAddResults': lambda: self.setRequestState('addingResults'),
                'onRemoveDuplicateRecords': lambda: self.setRequestState('removingDuplicates')
            })
            self.setTicketProgressTo100AndMarkAsDone(progressHandler)
        self.state = 'finished'

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

