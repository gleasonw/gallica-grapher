from typing import List, Optional

from gallicaGetter.buildqueries.argToQueryTransformations import bundle_codes
from gallicaGetter.buildqueries.buildDateGrouping import build_date_grouping
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
from gallicaGetter.fetch.paperQuery import PaperQuery


def build_base_queries(
    terms: List[str] | str,
    endpoint_url: str,
    grouping: str,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    codes: Optional[List[str] | str] = None,
    link_term: Optional[str] = None,
    link_distance: Optional[int] = None,
) -> List[OccurrenceQuery | PaperQuery]:
    if not isinstance(terms, list):
        terms = [terms]
    if codes and not isinstance(codes, list):
        codes = [codes]
    base_queries = []
    for term in terms:
        for start, end in build_date_grouping(start_date, end_date, grouping):
            for code_bundle in bundle_codes(codes):
                base_queries.append(
                    OccurrenceQuery(
                        term=term,
                        codes=code_bundle,
                        start_date=start,
                        end_date=end,
                        endpoint_url=endpoint_url,
                        start_index=0,
                        num_records=1,
                        link_term=link_term,
                        link_distance=link_distance,
                    )
                )
    return base_queries


def build_base_queries_at_indices(queries, indices):
    indexed_queries = []
    if type(indices) is not list:
        indices = [indices]
    for index in indices:
        for query in queries:
            indexed_queries.append(query.make_copy(start_index=index, num_records=1))
    return indexed_queries
