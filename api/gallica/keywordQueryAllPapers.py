import datetime
from math import ceil

from recordBatch import RecordBatch
from keywordQuery import KeywordQuery
from concurrent.futures import ThreadPoolExecutor


class KeywordQueryAllPapers(KeywordQuery):
    def __init__(self,
                 searchTerm,
                 yearRange,
                 eliminateEdgePapers,
                 requestID,
                 progressTracker,
                 dbConnection):

        self.recordIndexChunks = []
        self.eliminateEdgePapers = eliminateEdgePapers
        super().__init__(searchTerm,
                         yearRange,
                         requestID,
                         progressTracker,
                         dbConnection)

        self.findNumTotalResults()

    def buildYearRangeQuery(self):
        lowYear = str(self.lowYear)
        highYear = str(self.highYear)
        self.baseQuery = (
            f'dc.date >= "{lowYear}" '
            f'and dc.date <= "{highYear}" '
            f'and (gallica all "{self.keyword}") '
            'and (dc.type all "fascicule") '
            'sortby dc.date/sort.ascending'
        )

    def buildDatelessQuery(self):
        self.baseQuery = (
            f'(gallica all "{self.keyword}") '
            'and (dc.type all "fascicule") '
            'sortby dc.date/sort.ascending'
        )

    def findNumTotalResults(self):
        tempBatch = RecordBatch(self.baseQuery,
                                self.gallicaHttpSession,
                                numRecords=1)
        self.estimateNumResults = tempBatch.getNumResults()
        return self.estimateNumResults

    def runSearch(self):
        workerPool = self.generateSearchWorkers(50)
        self.doSearch(workerPool)
        if self.eliminateEdgePapers:
            self.cullResultsFromEdgePapers()
        self.completeSearch()

    def generateSearchWorkers(self, numWorkers):
        iterations = ceil(self.estimateNumResults / 50)
        self.recordIndexChunks = \
            [(i * 50) + 1 for i in range(iterations)]
        executor = ThreadPoolExecutor(max_workers=numWorkers)
        return executor

    def doSearch(self, workers):
        with workers as executor:
            for result in executor.map(
                    self.sendWorkersToSearch,
                    self.recordIndexChunks):
                numResultsInBatch = len(result)
                self.updateProgress(numResultsInBatch)
                self.results.extend(result)

    def sendWorkersToSearch(self, startRecord):
        batch = RecordBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            startRecord=startRecord,
        )
        results = batch.getRecordBatch()
        return results

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
