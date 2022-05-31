from GettingAndGraphing.termQuery import *


class TermQuerySelectPapers(TermQuery):
    def __init__(self, searchTerm, newspaperList, yearRange, progressTracker, dbConnection):
        super().__init__(searchTerm, yearRange, progressTracker, dbConnection, newspaperList=newspaperList)

    def runSearch(self):
        self.parseNewspaperDictionary()
        self.findTotalResults()
        self.createQueryStringList()
        self.spawnWorkerSearchThreads()
        self.progressTrackerThread.setNumberRetrievedResults(len(self.collectedQueries))
        self.completeSearch()

    def createQueryStringList(self):
        for newspaper in self.newspaperDictionary:
            hitsInNewspaper = self.numResultsForEachPaper[newspaper]
            newspaperKey = self.newspaperDictionary[newspaper]
            numberOfQueriesToSend = ceil(hitsInNewspaper / 50)
            startRecord = 1
            for i in range(numberOfQueriesToSend):
                recordAndCode = [startRecord, newspaperKey]
                self.recordCodeStrings.append(recordAndCode)
                startRecord += 50

    def spawnWorkerSearchThreads(self):
        with ThreadPoolExecutor(max_workers=150) as executor:
            self.mapThreadsToWork(executor)

    def mapThreadsToWork(self, executor):
        progress = 0
        for result in executor.map(self.get50ResultsFromGallicaRecordIndex, self.recordCodeStrings):
            numberResultsInBatch = len(result)
            self.collectedQueries.extend(result)
            progress = progress + numberResultsInBatch
            self.updateProgress(progress, self.totalResults)

    def get50ResultsFromGallicaRecordIndex(self, recordStartAndCode):
        recordStart = recordStartAndCode[0]
        code = recordStartAndCode[1]
        queryFormatForPaper = self.baseQuery.format(newsKey=code)
        hunterForQuery = BatchGetter(queryFormatForPaper, recordStart, 50, self.gallicaHttpSession)
        try:
            hunterForQuery.getResultBatch()
        except ReadTimeout:
            print("Failed request!")
        results = hunterForQuery.getResultList()
        return results

    def findTotalResults(self):
        self.spawnWorkersForFindingTotalResults()
        self.generateNewspaperNumResultsDictionary()
        self.sumUpNewspaperResultsForTotalResults()
        self.progressTrackerThread.setNumberDiscoveredResults(self.totalResults)

    def spawnWorkersForFindingTotalResults(self):
        with ThreadPoolExecutor(max_workers=50) as executor:
            self.sendThreadsToFindTotalResults(executor)

    def sendThreadsToFindTotalResults(self, executor):
        for result in executor.map(self.findNumberResultsForOneNewspaper, self.newspaperDictionary):
            if result:
                self.paperNameCounts = self.paperNameCounts + result

    def findNumberResultsForOneNewspaper(self, newspaper):
        paperCounts = []
        newspaperCode = self.newspaperDictionary[newspaper]
        newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
        hunterForTotalNumberOfQueryResults = BatchGetter(newspaperQuery, 1, 1, self.gallicaHttpSession)
        numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
        if numberResultsForNewspaper > 0:
            paperCounts.append([newspaper, numberResultsForNewspaper, newspaperCode])
        return paperCounts

    def generateNewspaperNumResultsDictionary(self):
        self.newspaperDictionary.clear()
        for nameCountCode in self.paperNameCounts:
            paperName = nameCountCode[0]
            paperCount = nameCountCode[1]
            paperCode = nameCountCode[2]
            self.newspaperDictionary.update({paperName: paperCode})
            self.numResultsForEachPaper.update({paperName: paperCount})

    def sumUpNewspaperResultsForTotalResults(self):
        for paper in self.numResultsForEachPaper:
            self.totalResults += self.numResultsForEachPaper[paper]
