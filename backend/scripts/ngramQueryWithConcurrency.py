from math import ceil
from concurrent.futures import ThreadPoolExecutor
from .gallicaRecordBatch import GallicaKeywordRecordBatch
from .gallicaRecordBatch import GallicaRecordBatch
from scripts.cqlSelectStringForPapers import CQLSelectStringForPapers

NUM_WORKERS = 50
CHUNK_SIZE = 600


class NgramQueryWithConcurrency:

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
        self.workChunks = []

        self.establishYearRange(yearRange)
        self.gallicaHttpSession = session
        self.buildQuery()
        self.fetchNumTotalResults()

    def generateWorkChunks(self):
        pass

    def buildYearRangeQuery(self):
        pass

    def buildDatelessQuery(self):
        pass

    def fetchNumTotalResults(self):
        pass

    def getKeyword(self):
        return self.keyword

    def getRecords(self):
        return self.keywordRecords

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

    def runSearch(self):
        indecesToFetch = self.generateWorkChunks()
        chunkedIndeces = self.splitWorkChunks(indecesToFetch)
        with self.gallicaHttpSession:
            for chunk in indecesInChunks:
                recordsForChunk = self.doThreadedSearch(chunk)
                dbTranscation = DBTransaction()
                dbTransaction.insert(
                    recordsForChunk, 
                    'results', 
                    self.requestid
                )

    def splitWorkChunks(self, indecesToFetch):
        numChunks = ceil(len(indecesToFetch) / CHUNK_SIZE)
        chunks = []
        for i in range(numChunks):
            chunks.append(
                indecesToFetch[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            )
        return chunks
                

    def doThreadedSearch(self):
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for recordBatch in executor.map(self.doSearchChunk, self.workChunks):
                recordsForIndex = recordBatch.getRecords()
                if recordsForIndex:
                    randomPaper = recordBatch.getRandomPaper()
                    self.progressTracker(
                        randomPaper,
                        recordBatch.elapsedTime,
                        NUM_WORKERS
                    )
                    self.keywordRecords.extend(recordsForIndex)
                else:
                    # TODO: Ensure there are always records?
                    print("No records for batch")

    def doSearchChunk(self, workChunk):
        return GallicaKeywordRecordBatch(self.gallicaHttpSession, workChunk)


class NgramQueryWithConcurrencyAllPapers(NgramQueryWithConcurrency):

    def __init__(self,
                 searchTerm,
                 yearRange,
                 ticketID,
                 progressTracker,
                 dbConnection,
                 session):
        super().__init__(
            searchTerm,
            yearRange,
            ticketID,
            progressTracker,
            dbConnection,
            session)

    def buildYearRangeQuery(self):
        lowYear = str(self.lowYear)
        highYear = str(self.highYear)
        self.baseQuery = (
            f'dc.date >= "{lowYear}" '
            f'and dc.date <= "{highYear}" '
            f'and (gallica adj "{self.keyword}") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending'
        )

    def buildDatelessQuery(self):
        self.baseQuery = (
            f'(gallica adj "{self.keyword}") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending'
        )

    def fetchNumTotalResults(self):
        tempBatch = GallicaRecordBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            numRecords=1)
        self.estimateNumResults = tempBatch.getNumResults()
        return self.estimateNumResults

    def doSearchChunk(self, index):
        batch = GallicaKeywordRecordBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            startRecord=index)
        return batch

    def generateWorkChunks(self):
        iterations = ceil(self.estimateNumResults / 50)
        workChunks = [(i * 50) + 1 for i in range(iterations)]
        return workChunks


class NgramQueryWithConcurrencySelectPapers(NgramQueryWithConcurrency):
    def __init__(self,
                 searchTerm,
                 paperCodes,
                 yearRange,
                 ticketID,
                 progressTracker,
                 dbConnection,
                 session):

        self.paperCodes = paperCodes
        self.numResultsInQuery = {}
        self.baseQueries = []
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
            '({formattedCodeString}) '
            f'and dc.date >= "{lowYear}" '
            f'and dc.date <= "{highYear}" '
            f'and (gallica adj "{self.keyword}") '
            'sortby dc.date/sort.ascending'
        )

    def buildDatelessQuery(self):
        self.baseQuery = (
            '({formattedCodeString}) '
            f'and (gallica adj "{self.keyword}") '
            'sortby dc.date/sort.ascending'
        )

    def fetchNumTotalResults(self):
        self.setNumResultsForQueries()
        self.sumUpQueryResultsForTotalEstimate()

    def doSearchChunk(self, recordStartAndCode):
        recordStart = recordStartAndCode[0]
        code = recordStartAndCode[1]
        query = self.baseQuery.format(newsKey=code)
        batch = GallicaKeywordRecordBatch(
            query,
            self.gallicaHttpSession,
            startRecord=recordStart)
        return batch

    def recordsNotUnique(self, records):
        for record in records:
            for priorRecords in self.keywordRecords:
                if record.getUrl() == priorRecords.getUrl():
                    return True
        return False

    def generateWorkChunks(self):
        paperCQLStrings = self.generatePaperCQLWithMax20CodesEach()
        completeCQLStrings = [self.baseQuery.format(formattedCodeString=codeString) for codeString in paperCQLStrings]
        workChunks = self.generateIndicesForCQLQueries(completeCQLStrings)
        indexQueryPairs = []
        for chunk in workChunks:
            indexQueryPairs.extend(chunk)
        return indexQueryPairs

    def generatePaperCQLWithMax20CodesEach(self):
        for i in range(0, len(self.paperCodes), 20):
            codes = self.paperCodes[i:i + 20]
            formattedCodes = [f"{code[0]}_date" for code in codes]
            urlPaperString = 'arkPress all "' + '" or arkPress all "'.join(formattedCodes) + '"'
            yield urlPaperString

    def generateIndicesForCQLQueries(self, query):
        indexCodePairs = []
        for i in range(1, self.numResultsInQuery[query], 50):
            recordAndCode = (i, query)
            indexCodePairs.append(recordAndCode)
        yield indexCodePairs

    def setNumResultsForQueries(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            for numResults, query in executor.map(
                    self.fetchNumResultsForQuery,
                    self.baseQueries):
                self.numResultsInQuery[query] = numResults

    def fetchNumResultsForQuery(self, query):
        batch = GallicaRecordBatch(
            query,
            self.gallicaHttpSession,
            numRecords=1)
        numResults = batch.getNumResults()
        return numResults, query

    def sumUpQueryResultsForTotalEstimate(self):
        for query, count in self.numResultsInQuery.items():
            self.estimateNumResults += count
