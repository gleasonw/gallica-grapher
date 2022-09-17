from concurrent.futures import ThreadPoolExecutor
import urllib3
from urllib3.util.retry import Retry
from gallica.query import Query
import time

NUM_WORKERS = 60

retryStrategy = Retry(
    status_forcelist=[413, 429, 500, 502, 503, 504],
    backoff_factor=1
)


#TODO: experiment with a DB connection pool, insert results as they arrive to save memory
class Fetch:

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=32, read=244),
            retries=retryStrategy,
            maxsize=NUM_WORKERS
        )

    def fetchAll(self, queries) -> list[Query]:
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for data, _, _ in executor.map(self.get, queries):
                yield data

    def fetchAllAndTrackProgress(self, queries, tracker) -> list[Query]:
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for data, elapsed, term in executor.map(self.get, queries):
                tracker(data, elapsed, NUM_WORKERS)
                yield data, term

    def get(self, query) -> tuple:
        start = time.perf_counter()
        response = self.http.request(
            "GET",
            self.baseUrl,
            fields=query.getParams()
        )
        end = time.perf_counter()
        return response.data, end-start, query.term
