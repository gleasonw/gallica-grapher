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

    def fetchAll(self, queries, tracker=None) -> list:
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.api.get, queries):
                tracker and tracker(response.xml, response.elapsed, self.numWorkers)
                yield response
