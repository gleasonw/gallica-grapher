import gallicaGetter.parse.gallicaxmlparse as parser
from gallicaGetter.fetch.query import (
    ArkQueryForNewspaperYears,
    PaperQuery,
    OccurrenceQuery,
    SRUQuery
)
from gallicaGetter.buildqueries.dateGrouping import DateGrouping
import logging
from typing import Tuple, List

NUM_CODES_PER_BUNDLE = 10


def create_indexed_queries_from_root_queries(queries, limit=None) -> List[SRUQuery]:
    if limit:
        queries_with_num_results = ((query, limit) for query in queries)
    else:
        queries_with_num_results = get_num_results_for_query(queries)
    return index_queries_by_num_results(queries_with_num_results)


def index_queries_by_num_results(queries_num_results: List[Tuple[SRUQuery, int]]) -> List[SRUQuery]:
    indexed_queries = []
    for query, num_results in queries_num_results:
        for i in range(0, num_results, 50):
            base_data = query.get_cql_params()
            base_data['startIndex'] = i
            base_data["numRecords"] = min(50, num_results - i)
            indexed_queries.append(
                make_query(**base_data)
            )
    return indexed_queries


def get_num_results_for_query(queries, props) -> List[Tuple[SRUQuery, int]]:
    responses = props.api.get(queries)
    num_results_for_queries = [
        (response.query, parser.get_num_records(response.data))
        for response in responses
    ]
    return num_results_for_queries


def make_query(**kwargs):
    raise NotImplementedError


def build_queries_for_args(args) -> List[SRUQuery]:
    base_queries = build_base_queries(args)
    if args['grouping'] == 'all':
        return create_indexed_queries_from_root_queries(
            queries=base_queries,
            limit=args.get('numRecords')
        )
    if args['grouping'] == 'index_selection':
        for query in base_queries:
            query.numRecords = 1
    return base_queries


def build_base_queries(args) -> List[SRUQuery]:
    terms = args.get('terms')
    codes = args.get('codes')
    indices = args.get('startIndex', [0])
    if not isinstance(indices, list):
        indices = [indices]
    if not isinstance(terms, list):
        terms = [terms]
    if codes and not isinstance(codes, list):
        codes = [codes]
    return [
        make_query(
            term=term,
            startDate=startDate,
            endDate=endDate,
            searchMetaData=args,
            codes=codeBundle,
            start_index=startIndex
        )
        for term in terms
        for startDate, endDate in DateGrouping(
            args.get('startDate'),
            args.get('endDate'),
            args.get('grouping')
        )
        for codeBundle in bundle_codes(codes)
        for startIndex in indices
    ]


def bundle_codes(codes: List[str]) -> List[List[str]]:
    if codes is None or len(codes) == 0:
        return [[]]
    return [
        codes[i:i+NUM_CODES_PER_BUNDLE]
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE)
    ]


def make_query(props, **kwargs) -> OccurrenceQuery:
    codes = kwargs.get('codes')
    return OccurrenceQuery(
        term=kwargs.get('term'),
        searchMetaData=kwargs.get('searchMetaData'),
        startIndex=kwargs.get('startIndex'),
        numRecords=kwargs.get('numRecords'),
        codes=codes,
        startDate=kwargs.get('startDate'),
        endDate=kwargs.get('endDate'),
        endpoint=props.get_endpoint_url()
    )


def build_queries_for_args(codes):
    if codes == '':
        logging.warning('No codes provided (get(["..."]) or get("something") Proceeding to fetch all papers on Gallica. Stop me if you wish!')
        return build_sru_queries_for_all()
    if not isinstance(codes, list):
        codes = [codes]
    return build_sru_queries_for_codes(codes)


def build_sru_queries_for_codes(props, codes) -> List[PaperQuery]:
    sru_queries = []
    for i in range(0, len(codes), NUM_CODES_PER_BUNDLE):
        codes_for_query = codes[i:i + NUM_CODES_PER_BUNDLE]
        sru_query = PaperQuery(
            startIndex=0,
            numRecords=NUM_CODES_PER_BUNDLE,
            codes=codes_for_query,
            endpoint=props.get_endpoint_url()
        )
        sru_queries.append(sru_query)
    return sru_queries


def build_sru_queries_for_all(props) -> List[SRUQuery]:
    return create_indexed_queries_from_root_queries([
        PaperQuery(
            startIndex=0,
            numRecords=1,
            baseURL=props.get_endpoint_url()
        )
    ])


def build_ark_queries_for_codes(codes, props) -> List[ArkQueryForNewspaperYears]:
    if type(codes) == str:
        codes = [codes]
    return [
        ArkQueryForNewspaperYears(
            code=code,
            endpoint=props.get_endpoint_url()
        )
        for code in codes
    ]


def make_query(codes, start_index, num_records, props) -> PaperQuery:
    return PaperQuery(
        startIndex=start_index,
        numRecords=num_records,
        codes=codes,
        baseURL=props.get_endpoint_url()
    )


