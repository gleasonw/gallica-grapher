import threading
from scripts.ticket import Ticket
from scripts.utils.psqlconn import PSQLconn
from scripts.utils.gallicaSession import GallicaSession


class Request(threading.Thread):
    def __init__(self, tickets, requestID):
        self.session = GallicaSession().getSession()
        self.DBconnection = PSQLconn().getConn()
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.ticketDicts = tickets
        self.finished = False
        self.tooManyRecords = False
        self.ticketProgressStats = self.initProgressStats()
        self.records = []
        self.requestID = requestID
        self.estimateNumRecords = 0

        super().__init__()

    def run(self):

        def sumEstimateNumberRecordsForAllTickets(tickets):
            total = 0
            for tick in tickets:
                total += tick.getEstimateNumberRecords()
            return total

        requestTickets = self.generateRequestTickets()
        estimate = sumEstimateNumberRecordsForAllTickets(requestTickets)
        if self.estimateIsUnderRecordLimit(estimate):
            for ticket in requestTickets:
                ticket.run()
                self.records.extend(ticket.getRecords())
                self.setTicketProgressTo100AndMarkAsDone(ticket)
            self.finished = True
        else:
            self.estimateNumRecords = estimate
            self.tooManyRecords = True
        self.DBconnection.close()

    def generateRequestTickets(self):
        tickets = []
        for key, ticket in self.ticketDicts.items():
            requestToRun = Ticket(
                ticket,
                key,
                self,
                self.DBconnection,
                self.session)
            tickets.append(requestToRun)
        return tickets

    def estimateIsUnderRecordLimit(self, estimate):
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

    def initProgressStats(self):
        progressDict = {}
        for key, ticket in self.ticketDicts.items():
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
        numRetrieved = len(ticket.getRecords())
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
