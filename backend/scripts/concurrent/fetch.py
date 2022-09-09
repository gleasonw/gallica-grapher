import urllib3
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

NUM_WORKERS = 100

retryStrategy = Retry(
    total=10,
    status_forcelist=[413, 429, 500, 502, 503, 504],
    backoff_factor=1
)


def fetchAll(queries):
    http = urllib3.PoolManager(
        connect=34,
        read=245,
        maxsize=100,
        retries=retryStrategy,
    )
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(http.request, 'GET', query) for query in queries]
        results = [future.result() for future in futures]


def fetch(query):