from concurrent.futures import ThreadPoolExecutor
from typing import Generator, List

from gallicaGetter.fetch.gallicasession import GallicaSession
from gallicaGetter.fetch.gallicasession import Response
from gallicaGetter.fetch.progressUpdate import ProgressUpdate

NUM_WORKERS = 20


class ConcurrentFetch:
    def __init__(self, numWorkers=NUM_WORKERS):
        self.num_workers = numWorkers
        self.api = GallicaSession(numWorkers)

    def get(self, queries, onProgressUpdate=None):
        if type(queries) is not list:
            queries = [queries]
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for response in executor.map(self.api.get, queries):
                onProgressUpdate and onProgressUpdate(
                    ProgressUpdate(
                        elapsed_time=response.elapsed,
                        num_workers=NUM_WORKERS,
                        xml=response.xml,
                    )
                )
                yield response
