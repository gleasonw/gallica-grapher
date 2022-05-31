from GettingAndGraphing.termQuery import *


class TermQueryAllPapers(TermQuery):
    def __init__(self, searchTerm, yearRange, eliminateEdgePapers, progressTracker, dbConnection):
        super().__init__(searchTerm, yearRange, progressTracker, dbConnection, strictYearRange=eliminateEdgePapers)

    def runSearch(self):
        self.findTotalResults()
        self.updateProgress(100, 100)
        iterations = ceil(self.totalResults / 50)
        startRecordList = [(i * 50) + 1 for i in range(iterations)]
        with ThreadPoolExecutor(max_workers=50) as executor:
            for i, result in enumerate(executor.map(self.sendWorkersToSearch, startRecordList)):
                self.updateProgress(i, iterations)
                self.collectedQueries.extend(result)
        if self.eliminateEdgePapers:
            self.cullResultsFromEdgePapers()
        self.completeSearch()

    def sendWorkersToSearch(self, startRecord):
        hunter = BatchGetter(self.baseQuery, startRecord, 50, self.gallicaHttpSession)
        try:
            hunter.getResultBatch()
        except ReadTimeout:
            print("Failed request!")
        results = hunter.getResultList()
        return results

    # TODO: This syntax is confusing
    def findTotalResults(self):
        hunter = BatchGetter(self.baseQuery, 1, 1, self.gallicaHttpSession)
        self.totalResults = hunter.establishTotalHits(self.baseQuery, False)
        self.progressTrackerThread.setNumberDiscoveredResults(self.totalResults)

    def cullResultsFromEdgePapers(self):
        try:
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
        except psycopg2.DatabaseError as e:
            print(e)