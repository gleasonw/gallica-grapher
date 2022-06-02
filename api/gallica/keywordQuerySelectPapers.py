from math import ceil

from recordBatch import RecordBatch
from keywordQuery import KeywordQuery
import concurrent.futures


class KeywordQuerySelectPapers(KeywordQuery):
    def __init__(self,
                 searchTerm,
                 papers,
                 yearRange,
                 requestID,
                 progressTracker,
                 dbConnection):

        self.papers = papers
        self.paperCodeWithNumResults = {}
        self.batchQueryStrings = []

        super().__init__(searchTerm,
                         yearRange,
                         requestID,
                         progressTracker,
                         dbConnection)

        self.findNumResultsForEachPaper()
        self.sumUpPaperResultsForTotalEstimate()

    def buildYearRangeQuery(self):
        lowYear = str(self.lowYear)
        highYear = str(self.highYear)
        self.baseQuery = (
            'arkPress all "{newsKey}_date" '
            f'and dc.date >= "{lowYear}" '
            f'and dc.date <= "{highYear}" '
            f'and (gallica all "{self.keyword}") '
            'sortby dc.date/sort.ascending'
        )

    def buildDatelessQuery(self):
        self.baseQuery = (
            'arkPress all "{newsKey}_date" '
            f'and (gallica adj "{self.keyword}") '
            'sortby dc.date/sort.ascending'
        )

    def findNumResultsForEachPaper(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for paperCode, numResults in executor.map(
                        self.setNumberResultsInPaper,
                        self.papers):
                self.paperCodeWithNumResults[paperCode] = numResults

    def setNumberResultsInPaper(self, paper):
        paperCode = paper["code"]
        numResultQuery = self.baseQuery.format(newsKey=paperCode)
        batch = RecordBatch(numResultQuery,
                            self.gallicaHttpSession,
                            startRecord=1,
                            numRecords=1)
        numResults = batch.getNumResults()
        return paperCode, numResults

    def sumUpPaperResultsForTotalEstimate(self):
        for paperCode, count in self.paperCodeWithNumResults.items():
            self.estimateNumResults += count

    def runSearch(self):
        self.initBatchQueries()
        self.mapThreadsToSearch(50)
        self.completeSearch()

    def initBatchQueries(self):
        for paperCode, count in self.paperCodeWithNumResults.items():
            numBatches = ceil(count / 50)
            self.appendBatchQueryStringsForPaper(numBatches, paperCode)

    def appendBatchQueryStringsForPaper(self, numBatches, code):
        startRecord = 1
        for i in range(numBatches):
            recordAndCode = [startRecord, code]
            self.batchQueryStrings.append(recordAndCode)
            startRecord += 50

    def mapThreadsToSearch(self, numWorkers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=numWorkers) as executor:
            for result in executor.map(self.getResultsAtRecordIndex,
                                       self.batchQueryStrings):
                numResultsInBatch = len(result)
                self.results.extend(result)
                self.updateProgress(numResultsInBatch)

    def getResultsAtRecordIndex(self, recordStartAndCode):
        recordStart = recordStartAndCode[0]
        code = recordStartAndCode[1]
        query = self.baseQuery.format(newsKey=code)
        batch = RecordBatch(query,
                            self.gallicaHttpSession,
                            startRecord=recordStart,
                            numRecords=50)
        results = batch.getRecordBatch()
        return results
