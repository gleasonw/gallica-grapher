import threading

RECORD_LIMIT = 2000000
MAX_DB_SIZE = 10000000


class Request(threading.Thread):
    def __init__(self, requestID, ticketSearches, dbConn):
        self.ticketSearches = ticketSearches
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.finished = False
        self.tooManyRecords = False
        self.ticketProgressStats = {}
        self.requestID = requestID
        self.estimateNumRecords = 0
        self.DBconnection = dbConn
        super().__init__()

    def getProgressStats(self):
        return self.ticketProgressStats

    def run(self):
        self.initProgressStats()
        estimateRequestResults = sum(
            [
                tick.getEstimateNumResultsForTicket()
                for tick in self.ticketSearches
            ]
        )
        if self.estimateIsUnderLimit(estimateRequestResults):
            self.doAllSearches()
        else:
            self.estimateNumRecords = estimateRequestResults
            self.tooManyRecords = True
        self.DBconnection.close()

    def initProgressStats(self):
        progressDict = {}
        for search in self.ticketSearches:
            key = search.getTicketID()
            progressDict[key] = {
                'progress': 0,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 0,
                'randomPaper': None,
                'estimateSecondsToCompletion': 0
            }
        return progressDict

    def estimateIsUnderLimit(self, estimate):
        dbSpaceRemainingWithBuffer = MAX_DB_SIZE - self.getNumberRowsStoredInAllTables() - 10000
        return estimate < min(dbSpaceRemainingWithBuffer, RECORD_LIMIT)

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
            progressHandler.run()
            self.setTicketProgressTo100AndMarkAsDone(progressHandler)
        self.finished = True

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
            'estimateSecondsToCompletion': 0
        })

