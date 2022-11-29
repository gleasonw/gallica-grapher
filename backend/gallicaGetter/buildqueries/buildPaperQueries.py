import logging
from typing import List
from gallicaGetter.buildqueries.argToQueryTransformations import (
    NUM_CODES_PER_BUNDLE,
    build_indexed_queries,
    bundle_codes
)
from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from gallicaGetter.fetch.query import PaperQuery, SRUQuery


def build_paper_queries_for_codes(codes, endpoint_url: str, api: ConcurrentFetch) -> List[PaperQuery or SRUQuery]:
    def build_sru_queries_for_codes() -> List[PaperQuery]:
        sru_queries = []
        for code_bundle in bundle_codes(codes):
            sru_query = PaperQuery(
                startIndex=0,
                numRecords=NUM_CODES_PER_BUNDLE,
                codes=code_bundle,
                endpoint=endpoint_url
            )
            sru_queries.append(sru_query)
        return sru_queries

    if codes == '':
        logging.warning('No codes provided (get(["..."]) or get("something") Proceeding to fetch all papers on '
                        'Gallica. Stop me if you wish!')
        return build_indexed_queries(
            [
                PaperQuery(
                    startIndex=0,
                    numRecords=1,
                    baseURL=endpoint_url
                )
            ],
            api=api
        )
    if not isinstance(codes, list):
        codes = [codes]
    return build_sru_queries_for_codes()
