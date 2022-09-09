from math import ceil
from concurrent.futures import ThreadPoolExecutor
from gallicaRecordBatch import GallicaKeywordRecordBatch
from gallicaRecordBatch import GallicaRecordBatch
from scripts.cqlSelectStringForPapers import CQLSelectStringForPapers
from scripts.recordsToDBTransaction import RecordsToDBTransaction

NUM_WORKERS = 100
CHUNK_SIZE = 200


class NgramQueryWithConcurrency:

    @staticmethod
    def splitIntoCHUNK_SIZEchunks(items):
        numChunks = ceil(len(items) / CHUNK_SIZE)
        chunks = []
        for i in range(numChunks):
            chunks.append(
                items[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            )
        return chunks

    def __init__(self,
                 searchTerm,
                 yearRange,
                 ticketID,
                 requestID,
                 progressTracker,
                 dbConnection,
                 session):

        self.keyword = searchTerm
        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.baseQuery = None
        self.ticketID = ticketID
        self.requestID = requestID
        self.estimateNumResults = 0
        self.actualNumResults = 0
        self.progress = 0
        self.progressTracker = progressTracker
        self.dbConnection = dbConnection

        self.establishYearRange(yearRange)
        self.gallicaHttpSession = session

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

    def getEstimateNumResults(self):
        return self.estimateNumResults

    def getActualNumResults(self):
        return self.actualNumResults

    def establishYearRange(self, yearRange):
        if len(yearRange) == 2:
            self.lowYear = int(yearRange[0])
            self.highYear = int(yearRange[1])
            self.isYearRange = True
        else:
            self.isYearRange = False

    def buildBaseQuery(self):
        if self.isYearRange:
            self.buildYearRangeQuery()
        else:
            self.buildDatelessQuery()

    def runSearch(self):
        indicesToFetch = self.generateWorkChunks()
        chunkedIndices = NgramQueryWithConcurrency.splitIntoCHUNK_SIZEchunks(
            indicesToFetch
        )
        for chunk in chunkedIndices:
            recordsForChunk = self.doThreadedSearch(chunk)
            dbTransaction = RecordsToDBTransaction(
                self.requestID,
                self.dbConnection,
            )
            dbTransaction.insertResults(recordsForChunk)
            self.actualNumResults += len(recordsForChunk)
            del recordsForChunk

    def generateWorkChunks(self):
        return []

    def doThreadedSearch(self, chunkOfIndices):
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            recordsForChunk = []
            for recordBatch in executor.map(self.doSearchChunk, chunkOfIndices):
                recordsForIndex = recordBatch.getRecords()
                if recordsForIndex:
                    randomPaper = recordBatch.getRandomPaper()
                    self.progressTracker(
                        randomPaper,
                        recordBatch.elapsedTime,
                        NUM_WORKERS
                    )
                    recordsForChunk.extend(recordsForIndex)
                else:
                    # TODO: Ensure there are always records?
                    print("No records for batch")
            return recordsForChunk

    def doSearchChunk(self, workChunk):
        return GallicaKeywordRecordBatch(self.gallicaHttpSession, workChunk)


class NgramQueryWithConcurrencyAllPapers(NgramQueryWithConcurrency):

    def __init__(self,
                 searchTerm,
                 yearRange,
                 ticketID,
                 requestID,
                 progressTracker,
                 dbConnection,
                 session):
        super().__init__(
            searchTerm,
            yearRange,
            ticketID,
            requestID,
            progressTracker,
            dbConnection,
            session)
        self.buildBaseQuery()
        self.fetchNumTotalResults()

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
            self.ticketID,
            self.keyword,
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
                 requestID,
                 progressTracker,
                 dbConnection,
                 session):

        self.paperCodes = paperCodes
        self.numResultsInQueries = {}
        self.baseQueries = []
        self.batchQueryStrings = []

        super().__init__(searchTerm,
                         yearRange,
                         ticketID,
                         requestID,
                         progressTracker,
                         dbConnection,
                         session)
        self.buildBaseQuery()
        self.buildQueriesForPaperCodes()
        self.fetchNumTotalResults()

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

    def buildQueriesForPaperCodes(self):
        paperSelectCQLStrings = CQLSelectStringForPapers(self.paperCodes).cqlSelectStrings
        self.baseQueries = [
            self.baseQuery.format(formattedCodeString=codeString)
            for codeString in paperSelectCQLStrings
        ]

    def fetchNumTotalResults(self):
        self.setNumResultsForQueries()
        self.sumUpQueryResultsForTotalEstimate()

    def setNumResultsForQueries(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            for numResults, query in executor.map(
                    self.fetchNumResultsForQuery,
                    self.baseQueries):
                firstCode = query[14:25]
                self.numResultsInQueries[firstCode] = numResults

    def fetchNumResultsForQuery(self, query):
        batch = GallicaRecordBatch(
            query,
            self.gallicaHttpSession,
            numRecords=1)
        numResults = batch.getNumResults()
        return numResults, query

    def sumUpQueryResultsForTotalEstimate(self):
        for query, count in self.numResultsInQueries.items():
            self.estimateNumResults += count

    def generateWorkChunks(self):
        indexedQueryBatches = self.generateIndicesForCQLQueries()
        collapsedIndexQueryPairs = []
        for queryBatch in indexedQueryBatches:
            collapsedIndexQueryPairs.extend(queryBatch)
        return collapsedIndexQueryPairs

    def generateIndicesForCQLQueries(self):
        for query in self.baseQueries:
            yield self.getIndicesForCQLQuery(query)

    def getIndicesForCQLQuery(self, query):
        indexCodePairs = []
        firstCodeInQuery = query[14:25]
        for i in range(1, self.numResultsInQueries[firstCodeInQuery], 50):
            recordAndCode = [i, query]
            indexCodePairs.append(recordAndCode)
        return indexCodePairs

    def doSearchChunk(self, recordStartAndCode):
        recordStart = recordStartAndCode[0]
        code = recordStartAndCode[1]
        query = self.baseQuery.format(formattedCodeString=code)
        batch = GallicaKeywordRecordBatch(
            query,
            self.ticketID,
            self.keyword,
            self.gallicaHttpSession,
            startRecord=recordStart)
        return batch
