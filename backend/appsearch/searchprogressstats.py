from math import ceil
from gallicaxmlparse import GallicaXMLparse
from averageResponseTime import AverageResponseTime


def initProgressStats(ticketID, grouping):
    return SearchProgressStats(
        ticketID=ticketID,
        grouping=grouping,
        parse=GallicaXMLparse(),
    )


class SearchProgressStats:

    def __init__(
            self,
            ticketID,
            grouping,
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
        self.grouping = grouping
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
            'state': self.state,
            'grouping': self.grouping
        }

    def setGrouping(self, grouping):
        self.grouping = grouping

    def setNumRecordsToFetch(self, numRecordsToFetch):
        self.numRecordsToFetch = numRecordsToFetch

    def setState(self, state):
        self.state = state

    def update(self, progressStats):
        if not self.numBatches:
            self.state = "RUNNING"
            self.numBatches = ceil(self.numRecordsToFetch / 50) if self.grouping == 'all' else self.numRecordsToFetch
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
        self.numResultsRetrieved = self.numBatchesRetrieved * 50 if self.grouping == 'all' else self.numBatchesRetrieved
        self.estimateSecondsToCompletion = self.getEstimateSecondsToCompletion(numWorkers)
        self.randomPaperForDisplay = self.parse.getOnePaperFromRecordBatch(xml)

    def getEstimateSecondsToCompletion(self, numWorkers):
        numCycles = (self.numBatches - self.numBatchesRetrieved) / numWorkers
        estimateSecondsToCompletion = self.averageResponseTime.get() * numCycles
        return estimateSecondsToCompletion
