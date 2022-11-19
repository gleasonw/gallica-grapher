from concurrent.futures import ThreadPoolExecutor
from gallicaGetter.fetch.gallicasession import GallicaSession

NUM_WORKERS = 20


class ConcurrentFetch:

    def __init__(self, numWorkers=NUM_WORKERS):
        self.numWorkers = numWorkers
        self.api = GallicaSession(maxSize=numWorkers)

    def get(self, queries, onUpdateProgress=None) -> list:
        if type(queries) is not list:
            queries = [queries]
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.api.get, queries):
                onUpdateProgress and onUpdateProgress(
                    {
                        "elapsedTime": response.elapsed,
                        "numWorkers": self.numWorkers,
                        "xml": response.data,
                    }
                )
                yield response
