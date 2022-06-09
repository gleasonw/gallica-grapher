from math import ceil

from .keywordQuery import KeywordQueryAllPapers
from .keywordQuery import KeywordQuerySelectPapers


class TicketQuery:

    def __init__(self,
                 ticket,
                 key,
                 progresstrack,
                 dbconnection,
                 session):

        self.keywords = ticket["terms"]
        self.papersAndCodes = ticket["papersAndCodes"]
        self.yearRange = ticket["dateRange"]
        self.ticketID = key
        self.progressThread = progresstrack
        self.connectionToDB = dbconnection
        self.session = session
        self.keywordQueries = []
        self.topPapers = []
        self.totalResults = 0
        self.numBatchesRetrieved = 0
        self.numBatches = 0

    def run(self):
        self.initQueryObjects()
        self.getNumResults()
        self.numBatches = ceil(self.totalResults / 50)
        self.startQueries()
        self.sendTopPapersToRequestThread()

    def initQueryObjects(self):
        if self.papersAndCodes:
            for keyword in self.keywords:
                termQuery = self.genSelectPaperQuery(keyword)
                self.keywordQueries.append(termQuery)
        else:
            for keyword in self.keywords:
                termQuery = self.genAllPaperQuery(keyword)
                self.keywordQueries.append(termQuery)

    def genSelectPaperQuery(self, keyword):
        query = KeywordQuerySelectPapers(
            keyword,
            self.papersAndCodes,
            self.yearRange,
            self.ticketID,
            self.updateProgress,
            self.connectionToDB,
            self.session)
        return query

    def genAllPaperQuery(self, keyword):
        query = KeywordQueryAllPapers(
            keyword,
            self.yearRange,
            self.ticketID,
            self.updateProgress,
            self.connectionToDB,
            self.session)
        return query

    def getNumResults(self):
        for query in self.keywordQueries:
            numResultsForKeyword = query.getEstimateNumResults()
            self.totalResults += numResultsForKeyword

    def startQueries(self):
        for query in self.keywordQueries:
            query.runSearch()

    def updateProgress(self):
        self.numBatchesRetrieved += 1
        progressPercent = self.numBatchesRetrieved/self.numBatches
        progressPercent *= 100
        progressPercent = int(progressPercent)
        self.progressThread.setProgress(progressPercent)

    def sendTopPapersToRequestThread(self):
        for termQuery in self.keywordQueries:
            topPapers = termQuery.getTopPapers()
            self.topPapers.append(topPapers)
        self.progressThread.setTopPapers(self.topPapers)
