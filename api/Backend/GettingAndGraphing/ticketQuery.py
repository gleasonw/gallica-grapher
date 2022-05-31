from Backend.GettingAndGraphing.termQuery import TermQueryOnSelectPapers
from Backend.GettingAndGraphing.termQuery import TermQueryOnAllPapers
from Backend.GettingAndGraphing.graphJSONmaker import GraphJSONmaker

import psycopg2


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
                 searchList,
                 newspaperList,
                 yearRange,
                 eliminateEdgePapers,
                 progressTrackerThread):

        self.searchTermList = searchList
        self.newspaperList = newspaperList
        self.yearRange = yearRange
        self.eliminateEdgePapers = eliminateEdgePapers
        self.progressThread = progressTrackerThread
        self.requestID = progressTrackerThread.getRequestID()
        self.connectionToDB = TicketQuery.connectToDatabase()
        self.topPaperList = []

    def start(self):
        self.retrieveResults()
        self.closeDbConnectionForRequest()

    def closeDbConnectionForRequest(self):
        self.connectionToDB.close()
        self.connectionToDB = None

    def generateSelectPaperTermRetrievalObject(self):
        for searchTerm in self.searchTermList:
            resultGetterForTerm = ResultGetterForTermSelectPapers(
                searchTerm,
                self.newspaperList,
                self.yearRange,
                self.progressThread,
                self.connectionToDB)
            self.retrievalObjectList.append(resultGetterForTerm)

    def retrieveResultsForTicket(self):
        for searchTerm in self.searchTermList:
            self.resetProgress()
            self.sendTermToRequestThread(searchTerm)
            paramsForQuery = [
                searchTerm,
                self.yearRange,
                self.eliminateEdgePapers,
                self.progressThread,
                self.connectionToDB
            ]
            if self.newspaperList:
                termQuery = TermQueryOnSelectPapers(paramsForQuery)
            else:
                termQuery = TermQueryOnAllPapers(paramsForQuery)
            termQuery.runSearch()
            self.sendTopPapersToRequestThread()
            self.generateGraphJSON()

    def resetProgress(self):
        self.progressThread.setProgress(0)

    def sendTermToRequestThread(self, term):
        self.progressThread.setCurrentTerm(term)

    def generateGraphJSON(self):
        JSONmaker = GraphJSONmaker(
            self.requestID,
            self.connectionToDB,
            splitPapers=self.paperTrendLines,
            splitTerms=self.termTrendLines)
        JSONmaker.makeGraphJSON()
        graphJSON = JSONmaker.getGraphJSON()
        self.progressThread.setGraphJSON(graphJSON)

    def sendTopPapersToRequestThread(self):
        for termQuery in self.retrievalObjectList:
            topPapers = termQuery.getTopTenPapers()
            self.topPaperList.append(topPapers)
        self.progressThread.setTopPapers(self.topPaperList)
