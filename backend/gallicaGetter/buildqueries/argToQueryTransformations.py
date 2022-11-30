import gallicaGetter.parse.gallicaxmlparse as parser
from gallicaGetter.fetch.query import SRUQuery
from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from typing import Tuple, List

NUM_CODES_PER_BUNDLE = 10


def build_indexed_queries(queries: List[SRUQuery], api: ConcurrentFetch,
                          endpoint_url: str, limit=None) -> List[SRUQuery]:
    queries_with_num_results = limit and ((query, limit) for query in queries) or \
                               get_num_results_for_query(queries, api)
    return index_queries_by_num_results(queries_with_num_results, endpoint_url=endpoint_url)


def index_queries_by_num_results(queries_num_results: List[Tuple[SRUQuery, int]], endpoint_url: str) -> List[SRUQuery]:
    if not queries_num_results:
        return []
    make_query = type(queries_num_results[0][0])
    indexed_queries = []
    for query, num_results in queries_num_results:
        for i in range(0, num_results, 50):
            base_data = query.get_cql_params()
            base_data['startIndex'] = i
            base_data["numRecords"] = min(50, num_results - i)
            indexed_queries.append(
                make_query(
                    **base_data,
                    endpoint=endpoint_url
                )
            )
    return indexed_queries


def bundle_codes(codes: List[str]) -> List[List[str]]:
    if codes is None or len(codes) == 0:
        return [[]]
    return [
        codes[i:i + NUM_CODES_PER_BUNDLE]
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE)
    ]


def get_num_results_for_query(queries: List[SRUQuery], api: ConcurrentFetch) -> List[Tuple[SRUQuery, int]]:
    responses = api.get(queries)
    num_results_for_queries = [
        (response.query, parser.get_num_records(response.data))
        for response in responses
    ]
    return num_results_for_queries