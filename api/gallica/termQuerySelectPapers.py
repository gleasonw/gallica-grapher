from resultBatch import ResultBatch
from termQuery import TermQuery


class TermQuerySelectPapers(TermQuery):
    def __init__(self,
                 searchTerm,
                 papers,
                 yearRange,
                 requestID,
                 progressTracker,
                 dbConnection):

        super().__init__(searchTerm,
                         yearRange,
                         requestID,
                         progressTracker,
                         dbConnection,
                         papers=papers)

    def runSearch(self):
        self.createQueryStringList()
        self.mapThreadsToWork(50)
        self.completeSearch()

    def createQueryStringList(self):
        for newspaper in self.papersAndCodes:
            hitsInNewspaper = self.numResultsInEachPaper[newspaper]
            newspaperKey = self.papersAndCodes[newspaper]
            numberOfQueriesToSend = ceil(hitsInNewspaper / 50)
            startRecord = 1
            for i in range(numberOfQueriesToSend):
                recordAndCode = [startRecord, newspaperKey]
                self.indexAndCodeStrings.append(recordAndCode)
                startRecord += 50

    def mapThreadsToWork(self, numWorkers):
        with ThreadPoolExecutor(max_workers=numWorkers) as executor:
            for result in executor.map(self.getResultsAtRecordIndex,
                                       self.indexAndCodeStrings):
                numResultsInBatch = len(result)
                self.results.extend(result)
                self.updateProgress(numResultsInBatch)

    def getResultsAtRecordIndex(self, recordStartAndCode):
        recordStart = recordStartAndCode[0]
        code = recordStartAndCode[1]
        query = self.baseQuery.format(newsKey=code)
        batch = ResultBatch(query,
                            self.gallicaHttpSession,
                            startRecord=recordStart,
                            numRecords=50)
        results = batch.getResultBatch()
        return results

    def getTotalResults(self):
        self.spawnWorkersForFindingTotalResults()
        self.generateNewspaperNumResultsDictionary()
        self.sumUpNewspaperResultsForTotalResults()
        return self.totalResults

    def spawnWorkersForFindingTotalResults(self):
        with ThreadPoolExecutor(max_workers=50) as executor:
            self.sendThreadsToFindTotalResults(executor)

    def sendThreadsToFindTotalResults(self, executor):
        for result in executor.map(
                self.findNumberResultsInPaper,
                self.papersAndCodes):
            if result:
                self.paperNameCounts = self.paperNameCounts + result

    def findNumberResultsInPaper(self, newspaper):
        paperCountCode = []
        newspaperCode = self.papersAndCodes[newspaper]
        newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
        batch = ResultBatch(newspaperQuery,
                            self.gallicaHttpSession,
                            startRecord=1,
                            numRecords=1)
        numResults = batch.getNumResults()
        if numResults > 0:
            paperCountCode.append([newspaper,
                                   numResults,
                                   newspaperCode])
        return paperCountCode

    def generateNewspaperNumResultsDictionary(self):
        self.papersAndCodes.clear()
        for nameCountCode in self.paperNameCounts:
            paperName = nameCountCode[0]
            paperCount = nameCountCode[1]
            paperCode = nameCountCode[2]
            self.papersAndCodes.update({paperName: paperCode})
            self.numResultsInEachPaper.update({paperName: paperCount})

    def sumUpNewspaperResultsForTotalResults(self):
        for paper in self.numResultsInEachPaper:
            self.totalResults += self.numResultsInEachPaper[paper]
