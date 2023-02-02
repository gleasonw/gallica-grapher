from concurrent.futures import ThreadPoolExecutor
import time
from typing import Any
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from requests.exceptions import RetryError
from dataclasses import dataclass

from gallicaGetter.contentWrapper import ContentQuery
from gallicaGetter.fullTextWrapper import FullTextQuery
from gallicaGetter.issuesWrapper import IssuesQuery
from gallicaGetter.paperQuery import PaperQuery
from gallicaGetter.volumeQuery import VolumeQuery

NUM_WORKERS = 20


class ConcurrentFetch:
    """Fetches data for a list of queries in parallel."""

    def __init__(self, numWorkers=NUM_WORKERS):
        self.num_workers = numWorkers
        self.api = GallicaSession(numWorkers)

    def get(self, queries, on_update_progress=None):
        if type(queries) is not list:
            queries = [queries]
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for response in executor.map(self.api.get, queries):
                if on_update_progress:
                    on_update_progress(
                        ProgressUpdate(
                            elapsed_time=response.elapsed,
                            num_workers=NUM_WORKERS,
                            xml=response.xml,
                        )
                    )
                yield response


@dataclass(slots=True)
class Response:
    xml: bytes
    query: VolumeQuery | PaperQuery | IssuesQuery | ContentQuery | FullTextQuery
    elapsed: float


@dataclass(frozen=True, slots=True)
class ProgressUpdate:
    elapsed_time: float
    num_workers: int
    xml: bytes


class GallicaSession:
    """Gallica session built for each query batch fetch."""

    def __init__(self, maxSize):
        self.maxSize = maxSize
        retry_strategy = Retry(
            total=10,
            status_forcelist=[403, 429],
            backoff_factor=1,
            connect=20,
            read=20,
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_maxsize=self.maxSize,
            pool_connections=self.maxSize,
        )
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get(self, query) -> Response:
        start = time.perf_counter()
        try:
            response = self.session.get(
                query.endpoint_url, params=query.get_params_for_fetch()
            )
        except RetryError:
            print("retry error")
            return Response(b"", query, 0)
        end = time.perf_counter()
        if response.status_code != 200:
            print(f"Gallica HTTP response Error: {response.status_code}")
            return Response(b"", query, 0)
        return Response(xml=response.content, query=query, elapsed=end - start)
