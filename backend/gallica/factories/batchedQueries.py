class BatchedQueries:

    def __init__(self, batchSize):
        self.batchSize = batchSize

    def batchQueries(self, queries):
        chunks = []
        for i in range(0, len(queries), self.batchSize):
            chunks.append(queries[i:i + self.batchSize])
        return chunks

