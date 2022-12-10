from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from typing import Tuple, List, Union
from gallicaGetter.fetch.paperQuery import PaperQuery
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
import gallicaGetter.parse.parseXML as parseXML

NUM_CODES_PER_BUNDLE = 10


def build_indexed_queries(queries: Union[List[OccurrenceQuery], List[PaperQuery]],
                          api: ConcurrentFetch, limit=None) -> Union[List[OccurrenceQuery], List[PaperQuery]]:
    if limit:
        queries_with_num_results = ((query, limit) for query in queries)
    else:
        queries_with_num_results = get_num_results_for_queries(queries, api)
    return index_queries_by_num_results(queries_with_num_results)


def index_queries_by_num_results(
        queries_num_results: List[PaperQuery | OccurrenceQuery]) -> List[PaperQuery | OccurrenceQuery]:
    if not queries_num_results:
        return []
    indexed_queries = []
    for query in queries_num_results:
        for i in range(0, query.num_results, 50):
            indexed_queries.append(
                query.make_copy(start_index=i, num_records=50)
            )
    return indexed_queries


def bundle_codes(codes: List[str]) -> List[List[str]]:
    if codes is None or len(codes) == 0:
        return [[]]
    return [
        codes[i:i + NUM_CODES_PER_BUNDLE]
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE)
    ]


def get_num_results_for_queries(
        queries: List[PaperQuery | OccurrenceQuery],
        api: ConcurrentFetch) -> List[PaperQuery | OccurrenceQuery]:
    responses = api.get(queries)
    queries_with_num_results_state = []
    for response in responses:
        response.query.num_results = parseXML.get_num_records(response.xml)
        queries_with_num_results_state.append(response.query)
    return queries_with_num_results_state
