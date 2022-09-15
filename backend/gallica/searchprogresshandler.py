from math import ceil


class SearchProgressHandler:

    def __init__(self, ticket, searchDriver):
        self.search = searchDriver
        self.ticket = ticket
        self.actualTotalResults = 0
        self.numBatchesRetrieved = 0
        self.numBatches = 0
        self.averageResponseTime = None
        self.progressCallback = None

    def setProgressCallback(self, callback):
        self.progressCallback = callback

    def getTicketID(self):
        return self.ticket.key

    def run(self):
        self.search.setProgressTracker(self.updateProgressStats)
        self.search.search()

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
        ticketProgressStats = self.buildProgressStats(randomPaper, numWorkers)
        self.progressCallback.setTicketProgressStats(
            self.ticket.key,
            ticketProgressStats
        )

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

    def buildProgressStats(self, randomPaper, numWorkers):
        return {
            'progress': self.getPercentProgress(),
            'numResultsDiscovered': self.ticket.estimateNumResults,
            'numResultsRetrieved': self.numBatchesRetrieved * 50,
            'randomPaper': randomPaper,
            'estimateSecondsToCompletion': self.getEstimateSecondsToCompletion(numWorkers)
        }

