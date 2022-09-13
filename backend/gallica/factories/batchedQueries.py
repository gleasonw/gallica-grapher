class BatchedQueries:

    def __init__(self, queries, batchSize):
        self.queries = queries
        self.batchSize = batchSize
        self.batchedQueries = self.batchQueries()

    def batchQueries(self):
        allChunks = []
        chunk = []
        for query in self.queries:
            if len(chunk) < self.batchSize:
                chunk.append(query)
            else:
                allChunks.append(chunk)
                chunk = [query]
        return allChunks

