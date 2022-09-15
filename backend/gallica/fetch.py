from concurrent.futures import ThreadPoolExecutor
import urllib3
from urllib3.util.retry import Retry
from query import Query
import time

NUM_WORKERS = 100

retryStrategy = Retry(
    status_forcelist=[413, 429, 500, 502, 503, 504],
    backoff_factor=1
)


class Fetch:

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=32, read=244),
            retries=retryStrategy,
            maxsize=NUM_WORKERS
        )

    def fetchAll(self, queries) -> list[Query]:
        responses = []
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for result in executor.map(self.get, queries):
                responses.append(result)
        yield from responses

    def fetchAllAndTrackProgress(self, queries, tracker) -> list[Query]:
        responses = []
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for result in executor.map(self.get, queries):
                tracker(result, NUM_WORKERS)
                responses.append(result)
        yield from responses

    def get(self, query) -> Query:
        start = time.perf_counter()
        response = self.http.request(
            "GET",
            self.baseUrl,
            fields=query.getParams()
        )
        end = time.perf_counter()
        query.handleResponse(
            data=response.data,
            elapsed=end - start
        )
        return query
