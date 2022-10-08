from concurrent.futures import ThreadPoolExecutor
from fetchComponents.gallicaapi import GallicaAPI

NUM_WORKERS = 30


class ConcurrentFetch:

    def __init__(self, baseUrl, numWorkers=NUM_WORKERS):
        self.baseUrl = baseUrl
        self.numWorkers = numWorkers
        self.api = GallicaAPI(
            baseUrl=baseUrl,
            maxSize=numWorkers
        )

    def fetchAll(self, queries) -> list:
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.api.get, queries):
                yield response

    def fetchAllAndTrackProgress(self, queries, tracker) -> list:
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.api.get, queries):
                tracker(response.data, response.elapsed, self.numWorkers)
                yield response.data, response.query
