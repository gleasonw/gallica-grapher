class OccurrenceFetchDriver:

    #Plan: refactor ngramqueriesallpapers etc to be a simple query builder called by this class.
    def __init__(self, parse):
        pass

    #general methods
    @staticmethod
    def splitIntoCHUNK_SIZEchunks(items):
        numChunks = ceil(len(items) / CHUNK_SIZE)
        chunks = []
        for i in range(numChunks):
            chunks.append(
                items[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            )
        return chunks

    #remove duplicates using dict? if key error, remove? o(n)?
    def removeDuplicateRecords(self):
        pass

    #all papers methods

    def fetchNumTotalResults(self):
        tempBatch = GallicaRecordBatch(
            self.baseQuery,
            self.gallicaHttpSession,
            numRecords=1)
        self.estimateNumResults = tempBatch.getNumResults()
        return self.estimateNumResults

    #select papers methods

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

