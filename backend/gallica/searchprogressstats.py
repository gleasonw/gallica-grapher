from math import ceil
from averageResponseTime import AverageResponseTime


class SearchProgressStats:

    def __init__(
            self,
            ticketID,
            searchType,
            parse
    ):
        self.ticketID = ticketID
        self.numBatchesRetrieved = 0
        self.numBatches = None
        self.averageResponseTime = AverageResponseTime()
        self.numResultsRetrieved = 0
        self.estimateSecondsToCompletion = 0
        self.randomPaperForDisplay = None
        self.randomTextForDisplay = None
        self.progressPercent = 0
        self.state = 'NOT_STARTED'
        self.searchType = searchType
        self.numRecordsToFetch = 0
        self.parse = parse

    def get(self):
        return {
            'numResultsDiscovered': self.numRecordsToFetch,
            'numResultsRetrieved': self.numResultsRetrieved,
            'progressPercent': self.progressPercent,
            'estimateSecondsToCompletion': self.estimateSecondsToCompletion,
            'randomPaper': self.randomPaperForDisplay,
            'randomText': self.randomTextForDisplay,
            'state': self.state
        }

    def setNumRecordsToFetch(self, numRecordsToFetch):
        self.numRecordsToFetch = numRecordsToFetch

    def setState(self, state):
        self.state = state

    def update(self, progressStats):
        if not self.numBatches:
            self.state = "RUNNING"
            self.numBatches = ceil(self.numRecordsToFetch / 50) if self.searchType == 'all' else self.numRecordsToFetch
        self.updateProgressState(
            elapsedTime=progressStats['elapsedTime'],
            numWorkers=progressStats['numWorkers'],
            xml=progressStats['xml']
        )

    def updateProgressState(
            self,
            elapsedTime,
            numWorkers,
            xml
    ):
        self.numBatchesRetrieved += 1
        self.averageResponseTime.update(elapsedTime)
        self.progressPercent = ceil(self.numBatchesRetrieved / self.numBatches * 100)
        self.numResultsRetrieved = self.numBatchesRetrieved * 50 if self.searchType == 'all' else self.numBatchesRetrieved
        self.estimateSecondsToCompletion = self.getEstimateSecondsToCompletion(numWorkers)
        self.randomPaperForDisplay = self.parse.getOnePaperFromRecordBatch(xml)

    def getEstimateSecondsToCompletion(self, numWorkers):
        numCycles = (self.numBatches - self.numBatchesRetrieved) / numWorkers
        estimateSecondsToCompletion = self.averageResponseTime.get() * numCycles
        return estimateSecondsToCompletion
