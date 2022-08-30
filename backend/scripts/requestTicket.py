from math import ceil

from .ngramQueryWithConcurrency import NgramQueryWithConcurrencyAllPapers
from .ngramQueryWithConcurrency import NgramQueryWithConcurrencySelectPapers


class RequestTicket:

    def __init__(self,
                 ticket,
                 key,
                 progresstrack,
                 dbconnection,
                 session):

        self.terms = ticket["terms"]
        self.papersAndCodes = ticket["papersAndCodes"]
        self.dateRange = ticket["dateRange"]
        self.ticketID = key
        self.progressThread = progresstrack
        self.connectionToDB = dbconnection
        self.session = session
        self.termQueries = []
        self.topPapers = []
        self.totalResults = 0
        self.numBatchesRetrieved = 0
        self.numBatches = 0
        self.averageResponseTime = None
        self.records = []

    def getRecords(self):
        return self.records

    def getEstimateNumberRecords(self):
        if self.papersAndCodes:
            self.initQueryObjects(self.genSelectPaperQuery)
        else:
            self.initQueryObjects(self.genAllPaperQuery)
        self.sumResultsOfEachQuery()
        return self.totalResults

    def run(self):
        self.numBatches = ceil(self.totalResults / 50)
        for query in self.termQueries:
            query.runSearch()
            completedRecords = self.addKeywordAndTicketIDToRecords(
                query.getRecords(),
                query.getKeyword())
            self.records.extend(completedRecords)

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
            self.updateProgressStats,
            self.connectionToDB,
            self.session)
        return query

    def genAllPaperQuery(self, keyword):
        query = NgramQueryWithConcurrencyAllPapers(
            keyword,
            self.dateRange,
            self.ticketID,
            self.updateProgressStats,
            self.connectionToDB,
            self.session)
        return query

    def sumResultsOfEachQuery(self):
        for query in self.termQueries:
            numResultsForKeyword = query.getEstimateNumResults()
            self.totalResults += numResultsForKeyword

    def addKeywordAndTicketIDToRecords(self, records, keyword):
        for record in records:
            record.setKeyword(keyword)
            record.setTicketID(self.ticketID)
        return records

    def updateProgressStats(self, randomPaper, requestTime, numWorkers):
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

