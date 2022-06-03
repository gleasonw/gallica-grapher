import datetime
from math import ceil

import psycopg2

from requests_toolbelt import sessions

from timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from newspapers import Newspapers
from concurrent.futures import ThreadPoolExecutor
from recordBatch import RecordBatch


class KeywordQuery:

    @staticmethod
    def makeSession():
        gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter(timeout=25)
        gallicaHttpSession.mount("https://", adapter)
        return gallicaHttpSession

    def __init__(self,
                 searchTerm,
                 yearRange,
                 requestID,
                 progressTracker,
                 dbConnection):

        self.keyword = searchTerm
        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.baseQuery = None
        self.requestID = requestID
        self.estimateNumResults = 0
        self.progress = 0
        self.results = []
        self.topPapers = None
        self.currentEntryDataJustInCase = None
        self.progressTracker = progressTracker
        self.dbConnection = dbConnection

        self.establishYearRange(yearRange)
        self.gallicaHttpSession = KeywordQuery.makeSession()
        self.buildQuery()

    def getKeyword(self):
        return self.keyword

    def getTopPapers(self):
        return self.topPapers

    def getEstimateNumResults(self):
        return self.estimateNumResults

    def discoverTopPapers(self):
        cursor = self.dbConnection.cursor()
        cursor.execute("""
        
        SELECT count(requestResults.identifier) AS papercount, papers.papername
            FROM (SELECT identifier, paperid 
                    FROM results WHERE requestid = %s AND searchterm = %s) 
                    AS requestResults 
            INNER JOIN papers ON requestResults.paperid = papers.papercode 
            GROUP BY papers.papername 
            ORDER BY papercount DESC
            LIMIT 10;
                
        """, (self.requestID, self.keyword))
        self.topPapers = cursor.fetchall()

    def postRecordsToDB(self):
        for record in self.results:
            self.postRecord(record)

    def postRecord(self, record):
        try:
            self.insertOneResultToTable(record)
        except psycopg2.IntegrityError:
            self.addMissingPaperToDB(record)
            self.insertOneResultToTable(record)

    def insertOneResultToTable(self, record):
        cursor = self.dbConnection.cursor()
        url = record.get('url')
        paperCode = record.get('paperCode')
        date = record.get('date')
        cursor.execute("""
        
        INSERT INTO results 
            (identifier, date, searchterm, paperID, requestid)
        VALUES (%s, %s, %s, %s, %s);
        
        """, (
            url,
            date,
            self.keyword,
            paperCode,
            self.requestID)

                       )

    def addMissingPaperToDB(self, record):
        missingCode = record["paperCode"]
        paperQuery = Newspapers(self.dbConnection)
        paperQuery.addPaperToDBbyCode(missingCode)

    def establishYearRange(self, yearRange):
        if len(yearRange) == 2:
            self.lowYear = int(yearRange[0])
            self.highYear = int(yearRange[1])
            self.isYearRange = True
        else:
            self.isYearRange = False

    def buildQuery(self):
        if self.isYearRange:
            self.buildYearRangeQuery()
        else:
            self.buildDatelessQuery()

    def buildYearRangeQuery(self):
        pass

    def buildDatelessQuery(self):
        pass

    def completeSearch(self):
        if len(self.results) != 0:
            self.postRecordsToDB()
            self.discoverTopPapers()

    def updateProgress(self, addition):
        self.progressTracker(addition)


class KeywordQueryAllPapers(KeywordQuery):
    def __init__(self,
                 searchTerm,
                 yearRange,
                 requestID,
                 progressTracker,
                 dbConnection):

        self.recordIndexChunks = []
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
                    self.fetchBatchFromIndex,
                    self.recordIndexChunks):
                numResultsInBatch = len(result)
                self.updateProgress(numResultsInBatch)
                self.results.extend(result)

    def fetchBatchFromIndex(self, index):
        batch = RecordBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            startRecord=index,
        )
        results = batch.getRecordBatch()
        return results

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
        with ThreadPoolExecutor(max_workers=10) as executor:
            for paperCode, numResults in executor.map(
                    self.setNumberResultsInPaper,
                    self.papers):
                self.paperCodeWithNumResults[paperCode] = numResults

    def setNumberResultsInPaper(self, paper):
        paperCode = paper["paperCode"]
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
        with ThreadPoolExecutor(max_workers=numWorkers) as executor:
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
