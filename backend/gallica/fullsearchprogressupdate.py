from math import ceil
from gallica.responseTime import ResponseTime


class FullSearchProgressUpdate:

    def __init__(self, ticket, onProgressUpdate):
        self.ticket = ticket
        self.numBatchesRetrieved = 0
        self.numBatches = ceil(self.ticket.estimateNumResults / 50)
        self.averageResponseTime = ResponseTime()
        self.onProgressUpdate = onProgressUpdate

    def assembleProgressUpdate(
            self,
            elapsedTime,
            numWorkers,
            randomPaper
    ):
        self.numBatchesRetrieved += 1
        self.averageResponseTime.update(elapsedTime)
        self.onProgressUpdate(
            ticketKey=self.ticket.key,
            progressStats={
                'progress': self.getPercentProgress(),
                'numResultsDiscovered': self.ticket.estimateNumResults,
                'numResultsRetrieved': self.numBatchesRetrieved * 50,
                'randomPaper': randomPaper,
                'estimateSecondsToCompletion': self.getEstimateSecondsToCompletion(numWorkers),
                'active': 1
            }
        )

    def getPercentProgress(self):
        progressPercent = ceil(self.numBatchesRetrieved / self.numBatches * 100)
        return progressPercent

    def getEstimateSecondsToCompletion(self, numWorkers):
        numCycles = (self.numBatches - self.numBatchesRetrieved) / numWorkers
        estimateSecondsToCompletion = self.averageResponseTime.get() * numCycles
        return estimateSecondsToCompletion
