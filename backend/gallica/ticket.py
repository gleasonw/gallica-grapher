from math import ceil


class Ticket:

    def __init__(
            self,
            ticketID,
            requestID,
            search,
            fulfiller,
            progressThread
    ):
        self.search = search
        self.fulfiller = fulfiller
        self.ticketID = ticketID
        self.requestID = requestID
        self.estimateTotalResults = 0
        self.actualTotalResults = 0
        self.numBatchesRetrieved = 0
        self.numBatches = 0
        self.averageResponseTime = None
        self.progressThread = progressThread

    def getEstimateNumberRecords(self):
        return self.fulfiller.getEstimateNumberRecords()

    def run(self):
        self.fulfiller.setProgressTracker(self.updateProgressStats)
        self.search.getRecordsForOptions(self.fulfiller)

    def updateProgressStats(
            self,
            query,
            numWorkers,
            randomPaper
    ):
        self.numBatchesRetrieved += 1
        if self.averageResponseTime:
            self.updateAverageResponseTime(query.elapsedTime)
        else:
            self.averageResponseTime = query.elapsedTime
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

