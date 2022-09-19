from concurrent.futures import ThreadPoolExecutor
import urllib3
from urllib3.util.retry import Retry
from gallica.query import Query
from gallica.query import NumOccurrencesForTermQuery
from gallica.query import NumPapersOnGallicaQuery
from gallica.query import PaperQuery
from gallica.query import ArkQuery
import time

NUM_WORKERS = 45

retryStrategy = Retry(
    status_forcelist=[413, 429, 500, 502, 503, 504],
    backoff_factor=1
)


class ConcurrentFetch:

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=32, read=124),
            retries=retryStrategy,
            maxsize=NUM_WORKERS
        )

    def fetchAll(self, queries) -> list[Query]:
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for response in executor.map(self.get, queries):
                yield response

    def fetchAllAndTrackProgress(self, queries, tracker) -> list[Query]:
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for response in executor.map(self.get, queries):
                data = response[0]
                term = response[1]
                elapsed = response[2]
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
        returnsForQueryType = {
            Query: (response.data, query.term, end - start),
            NumOccurrencesForTermQuery: (response.data, query.cql),
            NumPapersOnGallicaQuery: (response.data, query.cql),
            PaperQuery: (response.data, query.cql),
            ArkQuery: (response.data, query.code)
        }
        return returnsForQueryType[type(query)]
