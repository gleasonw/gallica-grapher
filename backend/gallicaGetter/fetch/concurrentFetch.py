from concurrent.futures import ThreadPoolExecutor
from gallicaGetter.fetch.gallicasession import GallicaSession
from typing import List
from gallicaGetter.fetch.gallicasession import Response

NUM_WORKERS = 30


class ConcurrentFetch:

    def __init__(self, numWorkers=NUM_WORKERS):
        self.numWorkers = numWorkers
        self.api = GallicaSession(maxSize=numWorkers)

    def get(self, queries, onProgressUpdate=None) -> List[Response]:
        if type(queries) is not list:
            queries = [queries]
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.api.get, queries):
                onProgressUpdate and onProgressUpdate(
                    elapsed_time=response.elapsed,
                    num_workers=self.numWorkers,
                    xml=response.xml
                )
                yield response
