from math import ceil
from gallica.averageResponseTime import AverageResponseTime


class SearchProgressStats:

    def __init__(self, ticketID, searchType, numRecordsToFetch):
        self.ticketID = ticketID
        self.numBatchesRetrieved = 0
        self.numBatches = None
        self.averageResponseTime = AverageResponseTime()
        self.numResultsRetrieved = 0
        self.estimateSecondsToCompletion = 0
        self.randomPaperForDisplay = None
        self.randomTextForDisplay = None
        self.progressPercent = 0
        self.active = 0
        self.searchType = searchType
        self.numRecordsToFetch = numRecordsToFetch

    def get(self):
        return {
            'numResultsDiscovered': self.numRecordsToFetch,
            'numResultsRetrieved': self.numResultsRetrieved,
            'progressPercent': self.progressPercent,
            'estimateSecondsToCompletion': self.estimateSecondsToCompletion,
            'randomPaperForDisplay': self.randomPaperForDisplay,
            'randomTextForDisplay': self.randomTextForDisplay,
            'active': self.active
        }

    def update(self, progressStats):
        if not self.numBatches:
            self.doSetup(progressStats)
        else:
            self.updateProgressState(
                elapsedTime=progressStats['elapsedTime'],
                numWorkers=progressStats['numWorkers'],
                randomPaper=progressStats.get('randomPaper'),
                randomTextForDisplay=progressStats.get('randomTextForDisplay')
            )

    def doSetup(self, progressStats):
        self.active = 1
        self.numBatches = ceil(self.numRecordsToFetch / 50) if self.searchType == 'all' else self.numRecordsToFetch
        self.updateProgressState(
            elapsedTime=progressStats['elapsedTime'],
            numWorkers=progressStats['numWorkers'],
        )

    def updateProgressState(
            self,
            elapsedTime,
            numWorkers,
            randomPaper=None,
            randomTextForDisplay=None
    ):
        self.numBatchesRetrieved += 1
        self.averageResponseTime.update(elapsedTime)
        self.progressPercent = ceil(self.numBatchesRetrieved / self.numBatches * 100)
        self.numResultsRetrieved = self.numBatchesRetrieved * 50 if self.searchType == 'all' else self.numBatchesRetrieved
        self.estimateSecondsToCompletion = self.getEstimateSecondsToCompletion(numWorkers)
        if randomPaper:
            self.randomPaperForDisplay = randomPaper
        if randomTextForDisplay:
            self.randomTextForDisplay = randomTextForDisplay

    def getEstimateSecondsToCompletion(self, numWorkers):
        numCycles = (self.numBatches - self.numBatchesRetrieved) / numWorkers
        estimateSecondsToCompletion = self.averageResponseTime.get() * numCycles
        return estimateSecondsToCompletion
