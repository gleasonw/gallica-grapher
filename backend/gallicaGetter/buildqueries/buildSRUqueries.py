from typing import Dict, List, Tuple

from gallicaGetter.buildqueries.argToQueryTransformations import index_queries_by_num_results, bundle_codes
from gallicaGetter.buildqueries.dateGrouping import DateGrouping
from gallicaGetter.fetch.query import SRUQuery, OccurrenceQuery


def build_queries(args: Dict, endpoint_url: str, query_cache: List[Tuple[SRUQuery, int]] = None) -> List[SRUQuery]:
    if query_cache:
        return index_queries_by_num_results(query_cache)
    terms = args.get('terms')
    codes = args.get('codes')
    if not isinstance(terms, list):
        terms = [terms]
    if codes and not isinstance(codes, list):
        codes = [codes]
    queries = [
        OccurrenceQuery(
            term=term,
            startDate=startDate,
            endDate=endDate,
            searchMetaData=args,
            codes=codeBundle,
            endpoint=endpoint_url
        )
        for term in terms
        for startDate, endDate in DateGrouping(
            args.get('startDate'),
            args.get('endDate'),
            args.get('grouping')
        )
        for codeBundle in bundle_codes(codes)
    ]
    if args['grouping'] == 'index_selection':
        return build_index_sample_volume_queries_for_args(queries)
    return queries


def build_index_sample_volume_queries_for_args(base_queries: List[SRUQuery]) -> List[SRUQuery]:
    for query in base_queries:
        query.numRecords = 1
    return base_queries
