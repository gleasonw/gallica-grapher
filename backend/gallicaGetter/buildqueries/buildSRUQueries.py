from typing import Dict, List

from gallicaGetter.buildqueries.argToQueryTransformations import build_indexed_queries
from gallicaGetter.buildqueries.buildSRUqueries import build_queries
from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from gallicaGetter.fetch.query import SRUQuery


def build_indexed_volume_occurrence_queries_for_args(args: Dict,
                                                     api: ConcurrentFetch,
                                                     endpoint_url: str) -> List[SRUQuery]:
    base_queries = build_queries(args, endpoint_url)
    return build_indexed_queries(
        queries=base_queries,
        limit=args.get('numRecords'),
        api=api
    )
