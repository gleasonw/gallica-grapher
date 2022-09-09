from math import ceil

from .ngramQueryWithConcurrency import NgramQueryWithConcurrencyAllPapers
from .ngramQueryWithConcurrency import NgramQueryWithConcurrencySelectPapers


class Ticket:

    def __init__(self,
                 ticket,
                 ticketID,
                 requestID,
                 progresstrack,
                 dbconnection,
                 session):

        self.terms = ticket["terms"]
        self.papersAndCodes = list(map(
            lambda x: (x["code"]),
            ticket["papersAndCodes"]
        ))
        self.dateRange = ticket["dateRange"]
        self.ticketID = ticketID
        self.requestID = requestID
        self.progressThread = progresstrack
        self.connectionToDB = dbconnection
        self.session = session
        self.termQueries = []
        self.topPapers = []
        self.estimateTotalResults = 0
        self.actualTotalResults = 0
        self.numBatchesRetrieved = 0
        self.numBatches = 0
        self.averageResponseTime = None

    def getEstimateNumberRecords(self):
        if self.papersAndCodes:
            self.initQueryObjects(self.genSelectPaperQuery)
        else:
            self.initQueryObjects(self.genAllPaperQuery)
        self.sumResultsOfEachQuery()
        return self.estimateTotalResults

    def sumResultsOfEachQuery(self):
        for query in self.termQueries:
            numResultsForKeyword = query.getEstimateNumResults()
            self.estimateTotalResults += numResultsForKeyword

    def run(self):
        self.numBatches = ceil(self.estimateTotalResults / 50)
        for query in self.termQueries:
            query.runSearch()
            self.actualTotalResults += query.getActualNumResults()

    def initQueryObjects(self, generator):
        for keyword in self.terms:
            gallicaNgramOccurrenceQuery = generator(keyword)
            self.termQueries.append(gallicaNgramOccurrenceQuery)

    def genSelectPaperQuery(self, keyword):
        query = NgramQueryWithConcurrencySelectPapers(
            keyword,
            self.papersAndCodes,
            self.dateRange,
            self.ticketID,
            self.requestID,
            self.updateProgressStats,
            self.connectionToDB,
            self.session)
        return query

    def genAllPaperQuery(self, keyword):
        query = NgramQueryWithConcurrencyAllPapers(
            keyword,
            self.dateRange,
            self.ticketID,
            self.requestID,
            self.updateProgressStats,
            self.connectionToDB,
            self.session)
        return query


    def updateProgressStats(self, randomPaper, requestTime, numWorkers):
        self.numBatchesRetrieved += 1
        if self.averageResponseTime:
            self.updateAverageResponseTime(requestTime)
        else:
            self.averageResponseTime = requestTime
        ticketProgressStats = {
            'progress': self.getPercentProgress(),
            'numResultsDiscovered': self.estimateTotalResults,
            'numResultsRetrieved': self.numBatchesRetrieved*50,
            'randomPaper': randomPaper,
            'estimateSecondsToCompletion': self.getEstimateSecondsToCompletion(numWorkers)
        }
        self.progressThread.setTicketProgressStats(self.ticketID, ticketProgressStats)

    def updateAverageResponseTime(self, requestTime):
        self.averageResponseTime = (self.averageResponseTime + requestTime) / 2
        return self.averageResponseTime

    def getPercentProgress(self):
        progressPercent = ceil(self.numBatchesRetrieved / self.numBatches * 100)
        return progressPercent

    def getEstimateSecondsToCompletion(self, numWorkers):
        numCycles = (self.numBatches - self.numBatchesRetrieved) / numWorkers
        estimateSecondsToCompletion = self.averageResponseTime * numCycles
        return estimateSecondsToCompletion

