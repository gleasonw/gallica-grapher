import psycopg2

from keywordQuery import KeywordQueryAllPapers, KeywordQuerySelectPapers
from ticketGraphData import TicketGraphData


class TicketQuery:

    @staticmethod
    def connectToDatabase():
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        return conn

    def __init__(self,
                 keywords,
                 papers,
                 years,
                 edgepapers,
                 progressthread):

        self.keywords = keywords
        self.papers = papers
        self.yearRange = years
        self.eliminateEdgePapers = edgepapers
        self.progressThread = progressthread
        self.requestID = progressthread.getRequestID()
        self.connectionToDB = TicketQuery.connectToDatabase()
        self.topPapers = []
        self.termQueries = []
        self.totalResults = 0
        self.numRetrieved = 0

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
            self.connectionToDB
        )
        return query

    def genAllPaperQuery(self, keyword):
        query = KeywordQueryAllPapers(
            keyword,
            self.yearRange,
            self.eliminateEdgePapers,
            self.requestID,
            self.updateProgress,
            self.connectionToDB
        )
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
        self.progressThread.setProgress(progressPercent)

    def sendTopPapersToRequestThread(self):
        for termQuery in self.termQueries:
            topPapers = termQuery.getTopPapers()
            self.topPapers.append(topPapers)
        self.progressThread.setTopPapers(self.topPapers)

    def closeDbConnectionForRequest(self):
        self.connectionToDB.close()
        self.connectionToDB = None
