from concurrent.futures import ThreadPoolExecutor
from fetchComponents.fetch import Fetch

NUM_WORKERS = 30


class ConcurrentFetch:

    def __init__(self, baseUrl, numWorkers=NUM_WORKERS):
        self.baseUrl = baseUrl
        self.numWorkers = numWorkers
        self.fetch = Fetch(
            baseUrl=baseUrl,
            maxSize=numWorkers
        )

    def fetchAll(self, queries) -> list:
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.fetch.get, queries):
                yield response

    def fetchAllAndTrackProgress(self, queries, tracker) -> list:
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.fetch.get, queries):
                data = response[0]
                term = response[1]
                elapsed = response[2]
                tracker(data, elapsed, self.numWorkers)
                yield data, term
