from math import ceil


class SearchProgressHandler:

    def __init__(self, ticket, searchDriver):
        self.search = searchDriver
        self.ticket = ticket
        self.numBatchesRetrieved = 0
        self.numBatches = ceil(self.ticket.estimateNumResults / 50)
        self.averageResponseTime = None
        self.onUpdateProgress = None

    def getNumRetrievedForTicket(self):
        return self.ticket.numResultsRetrieved

    def getEstimateNumResultsForTicket(self):
        return self.ticket.estimateNumResults

    def setProgressCallback(self, callback):
        self.onUpdateProgress = callback

    def getTicketID(self):
        return self.ticket.key

    def run(self):
        self.search.setProgressTracker(self.updateProgressStats)
        self.search.search()

    def updateProgressStats(
            self,
            elapsedTime,
            numWorkers,
            randomPaper
    ):
        self.numBatchesRetrieved += 1
        if self.averageResponseTime:
            self.updateAverageResponseTime(elapsedTime)
        else:
            self.averageResponseTime = elapsedTime
        ticketProgressStats = self.buildProgressStats(randomPaper, numWorkers)
        self.onUpdateProgress(
            ticketKey=self.ticket.key,
            progressStats=ticketProgressStats
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
            'estimateSecondsToCompletion': self.getEstimateSecondsToCompletion(numWorkers),
            'active': 1
        }

