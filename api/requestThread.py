import threading
from gallica.requestTicket import RequestTicket
from gallica.db import DB
from gallica.gallicaSession import GallicaSession


class RequestThread(threading.Thread):
    def __init__(self, tickets):
        self.session = GallicaSession().getSession()
        self.DBconnection = DB().getConn()
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.tickets = tickets
        self.finished = False
        self.ticketProgressStats = self.initProgressStats()

        super().__init__()

    def run(self):
        for key, ticket in self.tickets.items():
            requestToRun = RequestTicket(
                ticket,
                key,
                self,
                self.DBconnection,
                self.session)
            requestToRun.run()
        self.finished = True
        self.DBconnection.close()

    def initProgressStats(self):
        progressDict = {}
        for key, ticket in self.tickets.items():
            progressDict[key] = {
                'progress': 0,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 0,
                'randomPaper': None
            }
        return progressDict

    def isFinished(self):
        return self.finished

    def setTicketProgressStats(self, ticketKey, progressStats):
        self.ticketProgressStats[ticketKey] = progressStats

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

if __name__ == "__main__":
    request = RequestThread(
        {
            '2': {
                'terms': ['brazza'],
                'papersAndCodes': [{'code': 'cb32895690j', 'paper': 'Gallica'}],
                'dateRange': []
                }
        }
    )
    request.run()
