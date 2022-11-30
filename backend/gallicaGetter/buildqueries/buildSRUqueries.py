from typing import Dict, List, Tuple
from gallicaGetter.buildqueries.argToQueryTransformations import bundle_codes
from gallicaGetter.buildqueries.buildDateGrouping import build_date_grouping
from gallicaGetter.fetch.query import SRUQuery, OccurrenceQuery


def build_base_queries(args: Dict, endpoint_url: str) -> List[SRUQuery]:
    terms = args.get('terms')
    codes = args.get('codes')
    if not isinstance(terms, list):
        terms = [terms]
    if codes and not isinstance(codes, list):
        codes = [codes]
    base_queries = []
    for term in terms:
        for start, end in build_date_grouping(
                args.get('startDate'),
                args.get('endDate'),
                args.get('grouping')):
            for code_bundle in bundle_codes(codes):
                base_queries.append(
                    OccurrenceQuery(
                        term=term,
                        codes=code_bundle,
                        startDate=start,
                        endDate=end,
                        endpoint=endpoint_url,
                        searchMetaData=args,
                        startIndex=0,
                        numRecords=1
                    )
                )
    return base_queries


def build_base_queries_at_indices(queries, indices, endpoint_url):
    indexed_queries = []
    if type(indices) is not list:
        indices = [indices]
    for index in indices:
        for query in queries:
            params = query.get_cql_params()
            indexed_queries.append(OccurrenceQuery(
                **params,
                startIndex=index,
                numRecords=1,
                endpoint=endpoint_url
            )
            )
    return indexed_queries
