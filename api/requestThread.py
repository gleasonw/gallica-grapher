import threading
from .gallica.requestTicket import TicketQuery
import psycopg2
from requests_toolbelt import sessions
from .gallica.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter


class RequestThread(threading.Thread):
    def __init__(self,
                 tickets):
        self.progress = 0
        self.currentID = ''
        self.graphJSONForTicket = None
        self.session = None
        self.DBconnection = None
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.tickets = tickets

        self.initGallicaSession()
        self.connectToDatabase()

        super().__init__()

    def run(self):
        for ticket in self.tickets:
            requestToRun = TicketQuery(ticket,
                                       self,
                                       self.DBconnection,
                                       self.session)
            requestToRun.run()
        self.DBconnection.close()

    def setProgress(self, amount):
        self.progress = amount

    def getProgress(self):
        return self.progress

    def setCurrentID(self, ticketID):
        self.currentID = ticketID

    def getCurrentID(self):
        return self.currentID

    def setNumDiscovered(self, total):
        self.numResultsDiscovered = total

    def getNumDiscovered(self):
        return self.numResultsDiscovered

    def setNumRetrieved(self, count):
        self.numResultsRetrieved = count

    def getNumRetrieved(self):
        return self.numResultsRetrieved

    def setTopPapers(self, papers):
        self.topPapersForTerms = papers

    def getTopPapers(self):
        return self.topPapersForTerms

    def setGraphJSON(self, json):
        self.graphJSONForTicket = json

    def getGraphJSON(self):
        return self.graphJSONForTicket

    def initGallicaSession(self):
        self.session = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter()
        self.session.mount("https://", adapter)

    def connectToDatabase(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        self.DBconnection = conn
