from math import ceil
from gallica.responseTime import ResponseTime


class ProgressUpdate:

    def __init__(self, ticketID, onProgressUpdate, totalRecords):
        self.ticketID = ticketID
        self.numBatchesRetrieved = 0
        self.numBatches = ceil(totalRecords / 50)
        self.averageResponseTime = ResponseTime()
        self.onProgressUpdate = onProgressUpdate
        self.numRecords = totalRecords

    def assembleProgressUpdate(
            self,
            elapsedTime,
            numWorkers,
            randomPaper=None
    ):
        self.numBatchesRetrieved += 1
        self.averageResponseTime.update(elapsedTime)
        self.onProgressUpdate(
            ticketKey=self.ticketID,
            progressStats={
                'progress': self.getPercentProgress(),
                'numResultsDiscovered': self.numRecords,
                'numResultsRetrieved': self.numBatchesRetrieved * 50,
                'randomPaper': randomPaper,
                'estimateSecondsToCompletion': self.getEstimateSecondsToCompletion(numWorkers),
                'active': 1
            }
        )

    def onSearchFinish(self, numResults):
        self.onProgressUpdate(
            ticketKey=self.ticketID,
            progressStats={
                'progress': 100,
                'numResultsDiscovered': numResults,
                'numResultsRetrieved': numResults,
                'estimateSecondsToCompletion': 0,
                'active': 0
            }
        )

    def getPercentProgress(self):
        progressPercent = ceil(self.numBatchesRetrieved / self.numBatches * 100)
        return progressPercent

    def getEstimateSecondsToCompletion(self, numWorkers):
        numCycles = (self.numBatches - self.numBatchesRetrieved) / numWorkers
        estimateSecondsToCompletion = self.averageResponseTime.get() * numCycles
        return estimateSecondsToCompletion
