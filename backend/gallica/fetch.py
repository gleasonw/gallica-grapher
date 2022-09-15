from concurrent.futures import ThreadPoolExecutor
import urllib3
from urllib3.util.retry import Retry
from query import Query

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
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            return list(executor.map(self.get, queries))

    def fetchAllAndTrackProgress(self, queries, tracker) -> list[Query]:
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            responses = []
            for result in executor.map(self.get, queries):
                tracker(result, NUM_WORKERS)
                responses.append(result)
            return responses

    def get(self, query) -> Query:
        params = self.getParamsFor(query)
        response = self.http.request(
            "GET",
            self.baseUrl,
            fields=params
        )
        query.responseXML = response.data
        query.elapsedTime = response.elapsed.total_seconds()
        return query

    def getParamsFor(self, query) -> dict:
        return {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": query.startIndex,
            "maximumRecords": query.numRecords,
            "collapsing": query.collapsing,
            "query": query.cql,
        }
