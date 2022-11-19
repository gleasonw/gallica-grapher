from gallicaGetter.parse.gallicaxmlparse import GallicaXMLparse
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


class SRUQueryBuilder:

    def __init__(self, props):
        self.props = props
        self.parser = GallicaXMLparse()

    def create_indexed_queries_from_root_queries(self, queries, limit=None) -> List[SRUQuery]:
        if limit:
            queries_with_num_results = ((query, limit) for query in queries)
        else:
            queries_with_num_results = self.get_num_results_for_query(queries)
        return self.index_queries_by_num_results(queries_with_num_results)

    def index_queries_by_num_results(self, queries_num_results: List[Tuple[SRUQuery, str]]) -> List[SRUQuery]:
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

    def get_num_results_for_query(self, queries) -> List[Tuple[SRUQuery, str]]:
        responses = self.props.api.get(queries)
        num_results_for_queries = [
            (response.query, self.parser.get_num_records(response.data))
            for response in responses
        ]
        return num_results_for_queries

    def make_query(self, **kwargs):
        raise NotImplementedError


class OccurrenceQueryBuilder(SRUQueryBuilder):

    def build_queries_for_args(self, args) -> List:
        base_queries = self.build_base_queries(args)
        if args['grouping'] == 'all':
            return self.create_indexed_queries_from_root_queries(
                queries=base_queries,
                limit=args.get('numRecords')
            )
        return base_queries

    def build_base_queries(self, args) -> List[SRUQuery]:
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

    def make_query(self, **kwargs) -> OccurrenceQuery:
        codes = kwargs.get('codes')
        return OccurrenceQuery(
            term=kwargs.get('term'),
            searchMetaData=kwargs.get('searchMetaData'),
            startIndex=kwargs.get('startIndex'),
            numRecords=kwargs.get('numRecords'),
            codes=codes,
            startDate=kwargs.get('startDate'),
            endDate=kwargs.get('endDate'),
            endpoint=self.props.get_endpoint_url()
        )


class PaperQueryBuilder(SRUQueryBuilder):

    def build_queries_for_args(self, codes):
        if codes == '':
            logging.warning('No codes provided (get(["..."]) or get("something") Proceeding to fetch all papers on Gallica. Stop me if you wish!')
            return self.build_SRU_queries_for_all()
        if not isinstance(codes, list):
            codes = [codes]
        return self.build_SRU_queries_for_codes(codes)

    def build_SRU_queries_for_codes(self, codes) -> List[PaperQuery]:
        sru_queries = []
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE):
            codes_for_query = codes[i:i + NUM_CODES_PER_BUNDLE]
            sru_query = PaperQuery(
                startIndex=0,
                numRecords=NUM_CODES_PER_BUNDLE,
                codes=codes_for_query,
                endpoint=self.props.get_endpoint_url()
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


