from typing import List, Optional
from gallicaGetter.concurrentFetch import ConcurrentFetch
from gallicaGetter.parse_xml import get_num_records_from_gallica_xml
from gallicaGetter.volumeQuery import VolumeQuery
from gallicaGetter.paperQuery import PaperQuery


def build_indexed_queries(
    queries: List[VolumeQuery] | List[PaperQuery],
    api: ConcurrentFetch,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[VolumeQuery] | List[PaperQuery]:
    if limit:
        queries_with_num_results = []
        for query in queries:
            new_query = query.make_copy(start_index=offset or 0, num_records=limit)
            queries_with_num_results.append(new_query)
    else:
        queries_with_num_results = get_num_results_for_queries(queries, api)
    return index_queries_by_num_results(
        queries_with_num_results, records_per_query=limit or 50
    )


def get_num_results_for_queries(
    queries: List[VolumeQuery] | List[PaperQuery], api: ConcurrentFetch
) -> List[PaperQuery] | List[VolumeQuery]:
    responses = api.get(queries)
    queries_with_num_results_state = []
    for response in responses:
        assert response.query is type(VolumeQuery) or type(PaperQuery)
        response.query.gallica_results_for_params = get_num_records_from_gallica_xml(
            response.xml
        )
        queries_with_num_results_state.append(response.query)
    return queries_with_num_results_state


def index_queries_by_num_results(
    queries_num_results: List[PaperQuery] | List[VolumeQuery],
    records_per_query: int = 50,
) -> List[PaperQuery] | List[VolumeQuery]:
    if not queries_num_results:
        return []
    indexed_queries = []
    for query in queries_num_results:
        for i in range(0, query.gallica_results_for_params, records_per_query):
            indexed_queries.append(
                query.make_copy(start_index=i, num_records=records_per_query)
            )
    return indexed_queries
