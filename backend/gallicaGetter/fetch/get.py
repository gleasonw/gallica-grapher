import time
from urllib3.util.retry import Retry
import urllib3


class Response:

    def __init__(self, data, query, elapsed):
        self.data = data
        self.query = query
        self.elapsed = elapsed


class Get:

    def __init__(self, maxSize=50):
        self.maxSize = maxSize
        self.http = self.buildUrllib3()

    def buildUrllib3(self):
        retryStrategy = Retry(
            status_forcelist=[500, 502, 503, 504],
            backoff_factor=1,
        )
        http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=30, read=123),
            retries=retryStrategy,
            maxsize=self.maxSize
        )
        return http

    def get(self, query) -> Response:
        start = time.perf_counter()
        response = self.http.request(
            "GET",
            query.get_endpoint_url(),
            fields=query.get_params_for_fetch()
        )
        end = time.perf_counter()
        if response.status != 200:
            print(f"Gallica HTTP response Error: {response.status}")
        return Response(
            data=response.data,
            query=query,
            elapsed=end - start
        )

