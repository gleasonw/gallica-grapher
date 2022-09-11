import urllib3
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

NUM_WORKERS = 100

retryStrategy = Retry(
    total=10,
    status_forcelist=[413, 429, 500, 502, 503, 504],
    backoff_factor=1
)

http = urllib3.PoolManager(
    connect=34,
    read=245,
    maxsize=100,
    retries=retryStrategy,
)


class Fetch:

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl

    def fetchAll(self, queries):
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for result in executor.map(self.fetch, queries):
                yield result

    def fetchAllAndTrackProgress(self, queries, tracker):
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for result in executor.map(self.fetch, queries):
                tracker(result, NUM_WORKERS)
                yield result

    def fetch(self, query):
        params = self.getParamsFor(query)
        response = http.request(
            "GET",
            self.baseUrl,
            fields=params
        )
        query.responseXML = response.data
        query.elapsedTime = response.elapsed.total_seconds()
        return query

    def getParamsFor(self, query):
        return {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": query.startIndex,
            "maximumRecords": query.numRecords,
            "collapsing": query.collapsing,
            "query": query.url,
        }