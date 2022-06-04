import psycopg2

from keywordQuery import KeywordQueryAllPapers
from keywordQuery import KeywordQuerySelectPapers
from requests_toolbelt import sessions
from timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter


class TicketQuery:

    def __init__(self,
                 keywords,
                 papers,
                 years,
                 progressthread):

        self.keywords = keywords
        self.papers = papers
        self.yearRange = years
        self.progressThread = progressthread
        self.requestID = progressthread.getRequestID()
        self.connectionToDB = None
        self.session = None
        self.topPapers = []
        self.termQueries = []
        self.totalResults = 0
        self.numRetrieved = 0

        self.connectToDatabase()
        self.initGallicaSession()

    def run(self):
        self.initQueryObjects()
        self.getNumResults()
        self.startQueries()
        self.sendTopPapersToRequestThread()
        self.closeDbConnectionForRequest()

    def initQueryObjects(self):
        for keyword in self.keywords:
            if self.papers:
                termQuery = self.genSelectPaperQuery(keyword)
            else:
                termQuery = self.genAllPaperQuery(keyword)
            self.termQueries.append(termQuery)

    def genSelectPaperQuery(self, keyword):
        query = KeywordQuerySelectPapers(
            keyword,
            self.papers,
            self.yearRange,
            self.requestID,
            self.updateProgress,
            self.connectionToDB,
            self.session)
        return query

    def genAllPaperQuery(self, keyword):
        query = KeywordQueryAllPapers(
            keyword,
            self.yearRange,
            self.requestID,
            self.updateProgress,
            self.connectionToDB,
            self.session)
        return query

    def getNumResults(self):
        for query in self.termQueries:
            numResultsForKeyword = query.getEstimateNumResults()
            self.totalResults += numResultsForKeyword

    def startQueries(self):
        for query in self.termQueries:
            keyword = query.getKeyword()
            self.sendTermToFrontend(keyword)
            query.runSearch()

    def sendTermToFrontend(self, term):
        self.progressThread.setCurrentTerm(term)

    def updateProgress(self, addition):
        self.numRetrieved += addition
        progressPercent = self.numRetrieved/self.totalResults
        progressPercent *= 100
        progressPercent = int(progressPercent)
        self.progressThread.setProgress(progressPercent)

    def sendTopPapersToRequestThread(self):
        for termQuery in self.termQueries:
            topPapers = termQuery.getTopPapers()
            self.topPapers.append(topPapers)
        self.progressThread.setTopPapers(self.topPapers)

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
        self.connectionToDB = conn

    def closeDbConnectionForRequest(self):
        self.connectionToDB.close()
        self.connectionToDB = None
