from resultBatch import ResultBatch
from termQuery import TermQuery


class TermQueryAllPapers(TermQuery):
    def __init__(self,
                 searchTerm,
                 yearRange,
                 eliminateEdgePapers,
                 requestID,
                 progressTracker,
                 dbConnection):

        self.indexSlices = []
        super().__init__(searchTerm,
                         yearRange,
                         requestID,
                         progressTracker,
                         dbConnection,
                         strictYearRange=eliminateEdgePapers)

    def runSearch(self):
        workerPool = self.generateSearchWorkers(50)
        self.doSearch(workerPool)
        if self.eliminateEdgePapers:
            self.cullResultsFromEdgePapers()
        self.completeSearch()

    def generateSearchWorkers(self, numWorkers):
        iterations = ceil(self.totalResults / 50)
        self.indexSlices = [(i * 50) + 1 for i in range(iterations)]
        executor = ThreadPoolExecutor(max_workers=numWorkers)
        return executor

    def doSearch(self, workers):
        with workers as executor:
            for i, result in enumerate(executor.map(self.sendWorkersToSearch, self.indexSlices)):
                numResultsInBatch = len(result)
                self.updateProgress(numResultsInBatch)
                self.results.extend(result)

    def sendWorkersToSearch(self, startRecord):
        batch = ResultBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            startRecord=startRecord,
        )
        results = batch.getResultBatch()
        return results

    def getTotalResults(self):
        tempBatch = ResultBatch(self.baseQuery,
                                self.gallicaHttpSession,
                                startRecord=1,
                                numRecords=1)
        self.totalResults = tempBatch.getNumResults()
        return self.totalResults

    def cullResultsFromEdgePapers(self):
        cursor = self.dbConnection.cursor()
        startYear = datetime.date(int(self.lowYear), 1, 1)
        endYear = datetime.date(int(self.highYear), 1, 1)
        cursor.execute("""
        DELETE FROM results 
            WHERE results.requestID = %s 
            AND
            results.paperID IN 
            (SELECT papercode FROM papers 
                WHERE (papers.startyear > %s AND papers.startyear < %s) 
                OR (papers.endyear < %s AND papers.endyear > %s));
        """, (self.requestID, startYear, endYear, endYear, startYear))
