from typing import List
from gallicaGetter.buildqueries.argToQueryTransformations import bundle_codes
from gallicaGetter.buildqueries.buildDateGrouping import build_date_grouping
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
from gallicaGetter.fetch.paperQuery import PaperQuery
from gallicaGetter.gallicaWrapper import SRUArgs


def build_base_queries(args: SRUArgs, endpoint_url: str) -> List[OccurrenceQuery | PaperQuery]:
    if not isinstance(args.terms, list):
        args.terms = [args.terms]
    if args.codes and not isinstance(args.codes, list):
        args.codes = [args.codes]
    base_queries = []
    for term in args.terms:
        for start, end in build_date_grouping(
                args.startDate,
                args.endDate,
                args.grouping):
            for code_bundle in bundle_codes(args.codes):
                base_queries.append(
                    OccurrenceQuery(
                        term=term,
                        codes=code_bundle,
                        start_date=start,
                        end_date=end,
                        endpoint=endpoint_url,
                        start_index=0,
                        num_records=1,
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
                start_index=index,
                num_records=1,
                endpoint=endpoint_url
            )
            )
    return indexed_queries
