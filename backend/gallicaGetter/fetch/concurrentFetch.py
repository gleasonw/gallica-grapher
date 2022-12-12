from concurrent.futures import ThreadPoolExecutor
from gallicaGetter.fetch.gallicasession import GallicaSession
from typing import List
from gallicaGetter.fetch.gallicasession import Response

NUM_WORKERS = 20


class ConcurrentFetch:

    def __init__(self, numWorkers=NUM_WORKERS):
        self.num_workers = numWorkers
        self.api = GallicaSession(numWorkers)

    def get(self, queries, onProgressUpdate=None) -> List[Response]:
        if type(queries) is not list:
            queries = [queries]
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for response in executor.map(self.api.get, queries):
                onProgressUpdate and onProgressUpdate(
                    elapsed_time=response.elapsed,
                    num_workers=NUM_WORKERS,
                    xml=response.xml
                )
                yield response
