from gallicaGetter.parse.gallicaxmlparse import GallicaXMLparse
from gallicaGetter.fetch.query import (
    ArkQueryForNewspaperYears,
    PaperQuery,
    ContentQuery,
    FullTextQuery,
    OccurrenceQuery,
    SRUQuery
)
from gallicaGetter.build.dateGrouping import DateGrouping
import logging
from typing import Tuple, List

NUM_CODES_PER_BUNDLE = 10


class QueryBuilder:

    def __init__(self, props):
        self.props = props
        self.parser = GallicaXMLparse()

    def create_indexed_queries_from_root_queries(self, queries, limit=None) -> List:
        if limit:
            queries_with_num_results = ((query, limit) for query in queries)
        else:
            queries_with_num_results = self.get_num_results_for_query(queries)
        return self.index_queries_by_num_results(queries_with_num_results)

    def index_queries_by_num_results(self, queries_num_results: List[Tuple[SRUQuery, str]]) -> list:
        indexed_queries = []
        for query, num_results in queries_num_results:
            num_results = int(num_results)
            for i in range(0, num_results, 50):
                base_data = query.get_cql_params()
                base_data['startIndex'] = i
                base_data["numRecords"] = min(50, num_results - i)
                indexed_queries.append(
                    self.make_query(**base_data)
                )
        return indexed_queries

    def get_num_results_for_query(self, queries) -> List:
        responses = self.props.api.get(queries)
        num_results_for_queries = [
            (response.query, self.parser.getNumRecords(response.data))
            for response in responses
        ]
        return num_results_for_queries

    def make_query(self, **kwargs):
        raise NotImplementedError


class OccurrenceQueryBuilder(QueryBuilder):

    def build_queries_for_args(self, args):
        base_queries = self.build_base_queries(args)
        if args['grouping'] == 'all':
            return self.create_indexed_queries_from_root_queries(
                queries=base_queries,
                limit=args.get('numRecords')
            )
        return base_queries

    def build_base_queries(self, args):
        terms = args.get('terms')
        codes = args.get('codes')
        if not isinstance(terms, list):
            terms = [terms]
        if codes and not isinstance(codes, list):
            codes = [codes]
        return [
            self.make_query(
                term=term,
                startDate=startDate,
                endDate=endDate,
                searchMetaData=args,
                codes=codeBundle,
            )
            for term in terms
            for startDate, endDate in DateGrouping(
                args.get('startDate'),
                args.get('endDate'),
                args.get('grouping')
            )
            for codeBundle in self.bundle_codes(codes)
        ]

    def bundle_codes(self, codes: List[str]) -> List[List[str]]:
        if codes is None or len(codes) == 0:
            return [[]]
        return [
            codes[i:i+NUM_CODES_PER_BUNDLE]
            for i in range(0, len(codes), NUM_CODES_PER_BUNDLE)
        ]

    #TODO: use fewer args, reference props instead
    def make_query(self, term, startDate, endDate, searchMetaData, startIndex=0, numRecords=1, codes=None):
        codes = codes or []
        return OccurrenceQuery(
            term=term,
            searchMetaData=searchMetaData,
            startIndex=startIndex,
            numRecords=numRecords,
            codes=codes,
            startDate=startDate,
            endDate=endDate,
            endpoint=self.props.get_endpoint_url()
        )


class PaperQueryBuilder(QueryBuilder):

    def build_queries_for_args(self, codes):
        if codes == '':
            logging.warning('No codes provided (get(["..."]) or get("something") Proceeding to fetch all papers on Gallica. Stop me if you wish!')
            return self.build_SRU_queries_for_all()
        if not isinstance(codes, list):
            codes = [codes]
        return self.build_SRU_queries_for_codes(codes)

    def build_SRU_queries_for_codes(self, codes):
        sru_queries = []
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE):
            codes_for_query = codes[i:i + NUM_CODES_PER_BUNDLE]
            sru_query = PaperQuery(
                startIndex=0,
                numRecords=NUM_CODES_PER_BUNDLE,
                codes=codes_for_query,
                baseURL=self.props.get_endpoint_url()
            )
            sru_queries.append(sru_query)
        return sru_queries

    def build_SRU_queries_for_all(self):
        return self.create_indexed_queries_from_root_queries([
            PaperQuery(
                startIndex=0,
                numRecords=1,
                baseURL=self.props.get_endpoint_url()
            )
        ])

    def build_ark_queries_for_codes(self, codes):
        if type(codes) == str:
            codes = [codes]
        return [
            ArkQueryForNewspaperYears(
                code=code,
                endpoint=self.props.get_endpoint_url()
            )
            for code in codes
        ]

    def make_query(self, codes, startIndex, numRecords):
        return PaperQuery(
            startIndex=startIndex,
            numRecords=numRecords,
            codes=codes,
            baseURL=self.props.get_endpoint_url()
        )


class ContentQueryBuilder:

    def __init__(self, props):
        self.props = props

    def build_query_for_ark_and_term(self, ark, term):
        return ContentQuery(
            ark=ark,
            term=term,
            endpoint=self.props.endpoint_url
        )


class FullTextQueryBuilder:

    def __init__(self, props):
        self.props = props

    def build_queries_for_ark_codes(self, ark_codes):
        if type(ark_codes) is not list:
            ark_codes = [ark_codes]
        return [
            FullTextQuery(
                ark=code,
                endpoint=self.props.endpoint_url
            )
            for code in ark_codes
        ]