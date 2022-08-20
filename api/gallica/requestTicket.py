from math import ceil

from .gallicaNgramOccurrenceQuery import GallicaNgramOccurrenceQueryAllPapers
from .gallicaNgramOccurrenceQuery import GallicaNgramOccurrenceQuerySelectPapers


class RequestTicket:

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
        self.averageResponseTime = None

    def run(self):
        if self.papersAndCodes:
            self.initQueryObjects(self.genSelectPaperQuery)
        else:
            self.initQueryObjects(self.genAllPaperQuery)
        self.sumResultsOfEachTicket()
        self.startQueries()

    def initQueryObjects(self, generator):
        for keyword in self.keywords:
            gallicaNgramOccurrenceQuery = generator(keyword)
            self.keywordQueries.append(gallicaNgramOccurrenceQuery)

    def genSelectPaperQuery(self, keyword):
        query = GallicaNgramOccurrenceQuerySelectPapers(
            keyword,
            self.papersAndCodes,
            self.yearRange,
            self.ticketID,
            self.updateProgressStats,
            self.connectionToDB,
            self.session)
        return query

    def genAllPaperQuery(self, keyword):
        query = GallicaNgramOccurrenceQueryAllPapers(
            keyword,
            self.yearRange,
            self.ticketID,
            self.updateProgressStats,
            self.connectionToDB,
            self.session)
        return query

    def sumResultsOfEachTicket(self):
        for query in self.keywordQueries:
            numResultsForKeyword = query.getEstimateNumResults()
            self.totalResults += numResultsForKeyword

    def startQueries(self):
        self.numBatches = ceil(self.totalResults / 50)
        for query in self.keywordQueries:
            query.runSearch()

    def updateProgressStats(self, randomPaper, requestTime):
        self.numBatchesRetrieved += 1
        if self.averageResponseTime:
            self.updateAverageResponseTime(requestTime)
        else:
            self.averageResponseTime = requestTime
        ticketProgressStats = {
            'progress': self.getPercentProgress(),
            'numResultsDiscovered': self.totalResults,
            'numResultsRetrieved': self.numBatchesRetrieved*50,
            'randomPaper': randomPaper,
            'estimateSecondsToCompletion': self.getEstimateSecondsToCompletion()
        }
        self.progressThread.setTicketProgressStats(self.ticketID, ticketProgressStats)

    def updateAverageResponseTime(self, requestTime):
        if self.averageResponseTime < requestTime < self.averageResponseTime + 10:
            self.averageResponseTime += requestTime
            self.averageResponseTime /= 2
        elif requestTime < self.averageResponseTime:
            self.averageResponseTime = requestTime

    def getPercentProgress(self):
        progressPercent = ceil(self.numBatchesRetrieved / self.numBatches * 100)
        return progressPercent

    def getEstimateSecondsToCompletion(self):
        estimate = self.averageResponseTime * (self.numBatches - self.numBatchesRetrieved)
        return estimate

