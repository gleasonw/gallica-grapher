from concurrent.futures import ThreadPoolExecutor

from .gallicasession import GallicaSession
from .progressUpdate import ProgressUpdate

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
                if onProgressUpdate:
                    onProgressUpdate(
                        ProgressUpdate(
                            elapsed_time=response.elapsed,
                            num_workers=NUM_WORKERS,
                            xml=response.xml,
                        )
                    )
                yield response
