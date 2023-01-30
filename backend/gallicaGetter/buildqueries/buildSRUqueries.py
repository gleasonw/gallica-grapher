from typing import List, Literal, Optional, Tuple

from gallicaGetter.buildqueries.argToQueryTransformations import bundle_codes
from gallicaGetter.buildqueries.buildDateGrouping import build_date_grouping
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
from gallicaGetter.fetch.paperQuery import PaperQuery


def build_base_queries(
    terms: List[str],
    endpoint_url: str,
    grouping: str,
    link: Optional[Tuple[str, int]] = None,
    source: Optional[Literal["book", "periodical", "all"]] = None,
    sort: Optional[Literal["date", "relevance"]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    codes: Optional[List[str]] = None,
    limit: Optional[int] = None,
    cursor: Optional[int] = None,
) -> List[OccurrenceQuery | PaperQuery]:
    """
    Builds a list of queries to be used to fetch records from Gallica.
    If pulling all records for the query, this query will be used to get the number of records and then
    spawn additional indexed queries to fetch all records in batches of 50.
    """
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
                        start_index=cursor or 0,
                        num_records=limit or 1,
                        link=link,
                        source=source,
                        sort=sort,
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
