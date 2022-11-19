import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests


class Response:

    def __init__(self, data, query, elapsed):
        self.data = data
        self.query = query
        self.elapsed = elapsed


class GallicaSession:

    def __init__(self, maxSize=50):
        self.maxSize = maxSize
        self.session = self.build_session()

    def build_session(self):
        retry_strategy = Retry(
            total=3,
            status_forcelist=[500, 502, 503, 504],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_maxsize=self.maxSize,
            pool_connections=self.maxSize
        )
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get(self, query) -> Response:
        start = time.perf_counter()
        response = self.session.get(
            query.get_endpoint_url(),
            params=query.get_params_for_fetch()
        )
        end = time.perf_counter()
        if response.status_code != 200:
            print(f"Gallica HTTP response Error: {response.status_code}")
        return Response(
            data=response.content,
            query=query,
            elapsed=end - start
        )

