import time
from gallicaGetter.response import Response
from urllib3.util.retry import Retry
import urllib3


class Get:

    def __init__(self, baseUrl, maxSize=50):
        self.baseUrl = baseUrl
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
            self.baseUrl,
            fields=query.getFetchParams()
        )
        end = time.perf_counter()
        if response.status != 200:
            print(f"Error: {response.status}")
            print(f"Error: {response.data}")
        return Response(
            data=response.data,
            query=query,
            elapsed=end - start
        )
