import threading


class Request(threading.Thread):
    def __init__(self, queries, requestID, makeTicket, dbConn):
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.keyedQueries = queries
        self.finished = False
        self.tooManyRecords = False
        self.ticketProgressStats = self.initProgressStats()
        self.requestID = requestID
        self.estimateNumRecords = 0
        self.makeTicket = makeTicket
        self.DBconnection = dbConn
        super().__init__()

    def run(self):
        requestTickets = self.makeRequestTickets()
        estimateRequestResults = sum(
            [tick.estimateNumResults for tick in requestTickets]
        )
        if self.estimateIsUnderLimit(estimateRequestResults):
            self.doAllSearches(requestTickets)
        else:
            self.estimateNumRecords = estimateRequestResults
            self.tooManyRecords = True
        self.DBconnection.close()

    def makeRequestTickets(self):
        tickets = []
        for ID, queries in self.keyedQueries.items():
            queries = self.makeTicket(queries, ID, self)
            tickets.append(queries)
        return tickets

    def estimateIsUnderLimit(self, estimate):
        dbSpaceRemainingWithBuffer = 10000000 - self.getNumberRowsInAllTables() - 10000
        absoluteLimit = 3000000
        return estimate < min(dbSpaceRemainingWithBuffer, absoluteLimit)

    def getNumberRowsInAllTables(self):
        with self.DBconnection.cursor() as curs:
            curs.execute(
                """
                SELECT sum(reltuples)::bigint AS estimate
                FROM pg_class
                WHERE relname IN ('results', 'papers');
                """
            )
            return curs.fetchone()[0]

    def doAllSearches(self, requestTickets):
        for ticket in requestTickets:
            ticket.run()
            self.setTicketProgressTo100AndMarkAsDone(ticket)
        self.finished = True

    def initProgressStats(self):
        progressDict = {}
        for key, ticket in self.keyedQueries.items():
            progressDict[key] = {
                'progress': 0,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 0,
                'randomPaper': None,
                'estimateSecondsToCompletion': 0
            }
        return progressDict

    def setTicketProgressStats(self, ticketKey, progressStats):
        self.ticketProgressStats[ticketKey] = progressStats

    def setTicketProgressTo100AndMarkAsDone(self, ticket):
        numRetrieved = ticket.actualTotalResults
        self.setTicketProgressStats(ticket.ticketID, {
            'progress': 100,
            'numResultsDiscovered': numRetrieved,
            'numResultsRetrieved': numRetrieved,
            'randomPaper': None,
            'estimateSecondsToCompletion': 0
        })

    def getProgressStats(self):
        return self.ticketProgressStats

    def setNumDiscovered(self, total):
        self.numResultsDiscovered = total

    def getNumDiscovered(self):
        return self.numResultsDiscovered

    def setNumActuallyRetrieved(self, count):
        self.numResultsRetrieved = count

    def getNumActuallyRetrieved(self):
        return self.numResultsRetrieved
