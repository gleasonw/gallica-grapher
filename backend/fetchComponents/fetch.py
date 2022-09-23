import time

from .query import *
from urllib3.util.retry import Retry
import urllib3


class Fetch:

    def __init__(self, baseUrl, maxSize=50):
        self.baseUrl = baseUrl
        self.maxSize = maxSize
        self.http = self.buildUrllib3()

    def buildUrllib3(self):
        retryStrategy = Retry(
            status_forcelist=[413, 429, 500, 502, 503, 504],
            backoff_factor=1
        )
        http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=30, read=102),
            retries=retryStrategy,
            maxsize=self.maxSize
        )
        return http

    def get(self, query) -> tuple:
        start = time.perf_counter()
        response = self.http.request(
            "GET",
            self.baseUrl,
            fields=query.getParams()
        )
        end = time.perf_counter()
        returnsForQueryType = {
            Query: (response.data, query.term, end - start),
            NumOccurrencesForTermQuery: (response.data, query.cql),
            NumPapersOnGallicaQuery: (response.data, query.cql),
            PaperQuery: (response.data, query.cql),
            ArkQueryForNewspaperYears: (response.data, query.code),
            OCRQuery: response.data
        }
        return returnsForQueryType[type(query)]


