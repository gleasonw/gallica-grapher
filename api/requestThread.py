import threading
from gallica.requestTicket import RequestTicket
from gallica.db import DB
from gallica.gallicaSession import GallicaSession


class RequestThread(threading.Thread):
    def __init__(self, tickets):
        self.progress = 0
        self.currentID = ''
        self.session = GallicaSession().getSession()
        self.DBconnection = DB().getConn()
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.tickets = tickets
        self.finished = False

        super().__init__()

    def run(self):
        for key, ticket in self.tickets.items():
            self.currentID = key
            requestToRun = RequestTicket(
                ticket,
                key,
                self,
                self.DBconnection,
                self.session)
            requestToRun.run()
        self.finished = True
        self.DBconnection.close()

    def isFinished(self):
        return self.finished

    def setProgress(self, amount):
        self.progress = amount

    def getProgress(self):
        return self.progress

    def getCurrentID(self):
        return self.currentID

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
