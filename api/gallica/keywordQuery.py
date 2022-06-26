from math import ceil
import io

from .newspaper import Newspaper
from concurrent.futures import ThreadPoolExecutor
from .recordBatch import KeywordRecordBatch
from .recordBatch import RecordBatch

# TODO: remove results with same date and code
class KeywordQuery:

    def __init__(self,
                 searchTerm,
                 yearRange,
                 ticketID,
                 progressTracker,
                 dbConnection,
                 session):

        self.keyword = searchTerm
        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.baseQuery = None
        self.ticketID = ticketID
        self.estimateNumResults = 0
        self.progress = 0
        self.keywordRecords = []
        self.progressTracker = progressTracker
        self.dbConnection = dbConnection

        self.establishYearRange(yearRange)
        self.gallicaHttpSession = session
        self.buildQuery()
        self.fetchNumTotalResults()

    def getKeyword(self):
        return self.keyword

    def getEstimateNumResults(self):
        return self.estimateNumResults

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

    # TODO: move state up?
    def postRecordsToHoldingResultsDB(self):
        with self.dbConnection.cursor() as curs:
            csvStream = self.generateResultCSVstream()
            curs.copy_from(
                csvStream,
                'holdingresults',
                sep='|',
                columns=(
                    'identifier',
                    'year',
                    'month',
                    'day',
                    'jstime',
                    'searchterm',
                    'paperid',
                    'requestid')
            )
            self.postMissingPapers(curs)
            self.copyResultsToFinalTable(curs)

    def generateResultCSVstream(self):

        def cleanCSVvalue(value):
            if value is None:
                return r'\N'
            return str(value).replace('|', '\\|')

        csvFileLikeObject = io.StringIO()
        for record in self.keywordRecords:
            yearMonDay = record.getDate()
            csvFileLikeObject.write(
                "|".join(map(cleanCSVvalue, (
                    record.getUrl(),
                    yearMonDay[0],
                    yearMonDay[1],
                    yearMonDay[2],
                    record.getJSTimestamp(),
                    self.keyword,
                    record.getPaperCode(),
                    self.ticketID
                ))) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject

    def postMissingPapers(self, curs):
        paperGetter = Newspaper(self.gallicaHttpSession)
        missingPapers = self.getMissingPapers(curs)
        paperGetter.sendTheseGallicaPapersToDB(missingPapers)

    def getMissingPapers(self, curs):
        curs.execute(
            """
            WITH papersInResults AS 
                (SELECT DISTINCT paperid 
                FROM holdingResults 
                WHERE requestid = %s)

            SELECT paperid FROM papersInResults
            WHERE paperid NOT IN 
                (SELECT code FROM papers);
            """
            , (self.ticketID,))
        return curs.fetchall()

    def copyResultsToFinalTable(self, curs):
        curs.execute(
            """
            WITH resultsForRequest AS (
                DELETE FROM holdingresults
                WHERE requestid = %s
                RETURNING identifier, year, month, day, jstime, searchterm, paperid, requestid
            )
            
            INSERT INTO results (identifier, year, month, day, jstime, searchterm, paperid, requestid)
                (SELECT * FROM resultsForRequest);
            """
            , (self.ticketID,))

    def buildYearRangeQuery(self):
        pass

    def buildDatelessQuery(self):
        pass

    def fetchNumTotalResults(self):
        pass


class KeywordQueryAllPapers(KeywordQuery):
    def __init__(self,
                 searchTerm,
                 yearRange,
                 ticketID,
                 progressTracker,
                 dbConnection,
                 session):
        self.recordIndexChunks = []
        super().__init__(searchTerm, yearRange, ticketID, progressTracker, dbConnection, session)

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

    def fetchNumTotalResults(self):
        tempBatch = RecordBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            numRecords=1)
        self.estimateNumResults = tempBatch.getNumResults()
        return self.estimateNumResults

    def runSearch(self):
        with self.gallicaHttpSession:
            workerPool = self.generateSearchWorkers(50)
            self.doSearch(workerPool)
            if self.keywordRecords:
                self.postRecordsToHoldingResultsDB()

    # TODO: isolate concurrent code, only one class should be responsible for talking to Gallica
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
                self.progressTracker()
                self.keywordRecords.extend(result)

    def fetchBatchFromIndex(self, index):
        batch = KeywordRecordBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            startRecord=index)
        results = batch.getRecordBatch()
        return results


class KeywordQuerySelectPapers(KeywordQuery):
    def __init__(self,
                 searchTerm,
                 papers,
                 yearRange,
                 ticketID,
                 progressTracker,
                 dbConnection,
                 session):

        self.papers = papers
        self.paperCodeWithNumResults = {}
        self.batchQueryStrings = []

        super().__init__(searchTerm,
                         yearRange,
                         ticketID,
                         progressTracker,
                         dbConnection,
                         session)

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
            f'and (gallica all "{self.keyword}") '
            'sortby dc.date/sort.ascending'
        )

    def fetchNumTotalResults(self):
        self.setNumResultsForEachPaper()
        self.sumUpPaperResultsForTotalEstimate()

    def setNumResultsForEachPaper(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            for paperCode, numResults in executor.map(
                    self.fetchNumberResultsInPaper,
                    self.papers):
                self.paperCodeWithNumResults[paperCode] = numResults

    def fetchNumberResultsInPaper(self, paper):
        paperCode = paper["code"]
        numResultQuery = self.baseQuery.format(newsKey=paperCode)
        batch = RecordBatch(
            numResultQuery,
            self.gallicaHttpSession,
            numRecords=1)
        numResults = batch.getNumResults()
        return paperCode, numResults

    def sumUpPaperResultsForTotalEstimate(self):
        for paperCode, count in self.paperCodeWithNumResults.items():
            self.estimateNumResults += count

    def runSearch(self):
        with self.gallicaHttpSession:
            self.createURLIndecesForEachPaper()
            self.mapThreadsToSearch(50)
            if self.keywordRecords:
                self.postRecordsToHoldingResultsDB()

    def createURLIndecesForEachPaper(self):
        for paperCode, count in self.paperCodeWithNumResults.items():
            numBatches = ceil(count / 50)
            self.appendBatchQueryStringsForPaper(numBatches, paperCode)

    def appendBatchQueryStringsForPaper(self, numBatches, code):
        for i in range(numBatches):
            recordAndCode = [1 + 50 * i, code]
            self.batchQueryStrings.append(recordAndCode)

    def mapThreadsToSearch(self, numWorkers):
        with ThreadPoolExecutor(max_workers=numWorkers) as executor:
            for result in executor.map(
                    self.getPaperResultsAtRecordIndex,
                    self.batchQueryStrings):
                self.keywordRecords.extend(result)
                self.progressTracker()

    def getPaperResultsAtRecordIndex(self, recordStartAndCode):
        recordStart = recordStartAndCode[0]
        code = recordStartAndCode[1]
        query = self.baseQuery.format(newsKey=code)
        batch = KeywordRecordBatch(
            query,
            self.gallicaHttpSession,
            startRecord=recordStart)
        results = batch.getRecordBatch()
        return results
