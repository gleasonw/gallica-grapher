import psycopg2
from GettingAndGraphing.termQueryAllPapers import TermQueryAllPapers
from GettingAndGraphing.termQuerySelectPapers import TermQuerySelectPapers
from GettingAndGraphing.ticketGraphData import TicketGraphData


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
                 yearRange,
                 eliminateEdgePapers,
                 progressTrackerThread):

        self.keywords = keywords
        self.papers = papers
        self.yearRange = yearRange
        self.eliminateEdgePapers = eliminateEdgePapers
        self.progressThread = progressTrackerThread
        self.requestID = progressTrackerThread.getRequestID()
        self.connectionToDB = TicketQuery.connectToDatabase()
        self.topPapers = []
        self.termQueries = []
        self.totalResults = 0
        self.numRetrieved = 0

    def run(self):
        self.initQueryObjects()
        self.getNumResults()
        self.initKeywordSearch()
        self.closeDbConnectionForRequest()
        self.sendTopPapersToRequestThread()
        self.generateGraphJSON()

    def initQueryObjects(self):
        for keyword in self.keywords:
            if self.papers:
                termQuery = self.genSelectPaperQuery(keyword)
            else:
                termQuery = self.genAllPaperQuery(keyword)
            self.termQueries.append(termQuery)

    def genSelectPaperQuery(self, keyword):
        query = TermQuerySelectPapers(
            keyword,
            self.papers,
            self.yearRange,
            self.requestID,
            self.updateProgress,
            self.connectionToDB
        )
        return query

    def genAllPaperQuery(self, keyword):
        query = TermQueryAllPapers(
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
            numResultsForKeyword = query.getTotalResults()
            self.totalResults += numResultsForKeyword

    def initKeywordSearch(self):
        for query in self.termQueries:
            keyword = query.getKeyword()
            self.sendTermToRequestThread(keyword)
            query.runSearch()

    def sendTermToRequestThread(self, term):
        self.progressThread.setCurrentTerm(term)

    def updateProgress(self, addition):
        self.numRetrieved += addition
        progressPercent = int(self.numRetrieved/self.totalResults)
        self.progressThread.setProgress(progressPercent)

    def generateGraphJSON(self):
        graphData = TicketGraphData(
            self.requestID,
            self.connectionToDB)
        graphJSON = graphData.getGraphJSON()
        self.progressThread.setGraphJSON(graphJSON)

    def sendTopPapersToRequestThread(self):
        for termQuery in self.termQueries:
            topPapers = termQuery.getTopTenPapers()
            self.topPapers.append(topPapers)
        self.progressThread.setTopPapers(self.topPapers)

    def closeDbConnectionForRequest(self):
        self.connectionToDB.close()
        self.connectionToDB = None
