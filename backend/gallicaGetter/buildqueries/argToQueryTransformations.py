from typing import List, Optional

from parse import parseXML as parseXML
from fetch.concurrentFetch import ConcurrentFetch
from fetch.occurrenceQuery import OccurrenceQuery
from fetch.paperQuery import PaperQuery

NUM_CODES_PER_BUNDLE = 10


def build_indexed_queries(
    queries: List[OccurrenceQuery] | List[PaperQuery],
    api: ConcurrentFetch,
    limit,
    offset,
) -> List[OccurrenceQuery] | List[PaperQuery]:
    if limit:
        queries_with_num_results = []
        for query in queries:
            new_query = query.make_copy(start_index=offset, num_records=limit)
            queries_with_num_results.append(new_query)
    else:
        queries_with_num_results = get_num_results_for_queries(queries, api)
    return index_queries_by_num_results(
        queries_with_num_results, records_per_query=limit or 50
    )


def index_queries_by_num_results(
    queries_num_results: List[PaperQuery] | List[OccurrenceQuery],
    records_per_query: int = 50,
) -> List[PaperQuery] | List[OccurrenceQuery]:
    if not queries_num_results:
        return []
    indexed_queries = []
    for query in queries_num_results:
        for i in range(0, query.num_results, records_per_query):
            indexed_queries.append(
                query.make_copy(start_index=i, num_records=records_per_query)
            )
    return indexed_queries


def bundle_codes(codes: Optional[List[str]]) -> List[List[str]]:
    if codes is None or len(codes) == 0:
        return [[]]
    return [
        codes[i : i + NUM_CODES_PER_BUNDLE]
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE)
    ]


def get_num_results_for_queries(
    queries: List[OccurrenceQuery] | List[PaperQuery], api: ConcurrentFetch
) -> List[PaperQuery] | List[OccurrenceQuery]:
    responses = api.get(queries)
    queries_with_num_results_state = []
    for response in responses:
        response.query.num_results = parseXML.get_num_records(response.xml)
        queries_with_num_results_state.append(response.query)
    return queries_with_num_results_state
