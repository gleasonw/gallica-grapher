class BatchedQueries:

    def __init__(self, batchSize):
        self.batchSize = batchSize

    def batchQueries(self, queries):
        allChunks = []
        chunk = []
        for query in queries:
            if len(chunk) < self.batchSize:
                chunk.append(query)
            else:
                allChunks.append(chunk)
                chunk = [query]
        return allChunks

