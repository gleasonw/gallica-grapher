from concurrent.futures import ThreadPoolExecutor
from gallica.get import Get

NUM_WORKERS = 30


class ConcurrentFetch:

    def __init__(self, baseUrl, numWorkers=NUM_WORKERS):
        self.baseUrl = baseUrl
        self.numWorkers = numWorkers
        self.api = Get(
            baseUrl=baseUrl,
            maxSize=numWorkers
        )

    #TODO: implement text snippets every 20 seconds or so. Fun way to pass the time
    def get(self, queries, onUpdateProgress=None) -> list:
        with ThreadPoolExecutor(max_workers=self.numWorkers) as executor:
            for response in executor.map(self.api.get, queries):
                onUpdateProgress and onUpdateProgress(
                    {
                        "elapsedTime": response.elapsed,
                        "numWorkers": self.numWorkers,
                        "xml": response.xml,
                    }
                )
                yield response
