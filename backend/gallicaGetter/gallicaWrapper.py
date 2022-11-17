from gallicaGetter.build.queryBuilder import (
    OccurrenceQueryBuilder,
    ContentQueryBuilder,
    PaperQueryBuilder,
    FullTextQueryBuilder
)
from gallicaGetter.parse.parseRecord import buildParser
from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from typing import List


class GallicaWrapper:
    def __init__(self, **kwargs):
        self.api = ConcurrentFetch(numWorkers=kwargs.get('numWorkers', 10))
        self.endpoint_url = self.get_endpoint_url()
        self.parser = None
        self.queryBuilder = self.get_query_builder()
        self.post_init(kwargs)

    def post_init(self, kwargs):
        pass

    def get(self, **kwargs):
        raise NotImplementedError(f'get() not implemented for {self.__class__.__name__}')

    def get_query_builder(self):
        raise NotImplementedError(f'buildQueryBuilder() not implemented for {self.__class__.__name__}')

    def get_endpoint_url(self):
        raise NotImplementedError(f'getBaseURL() not implemented for {self.__class__.__name__}')
        
    def fetch_from_queries(self, queries, parser, onUpdateProgress=None):
        raw_response = self.api.get(
            queries,
            onUpdateProgress=onUpdateProgress
        )
        records = parser.parseResponsesToRecords(raw_response)
        return records

    def get_parser(self):
        pass


class SRUWrapper(GallicaWrapper):

    def post_init(self, kwargs):
        self.group_record_parser = buildParser(
            desiredRecord='groupedCount',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )
        self.solo_record_parser = buildParser(
            desiredRecord='occurrence',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )

    def get_query_builder(self):
        return OccurrenceQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, terms, onUpdateProgress=None, generate=False, queriesWithCounts=None, **kwargs) -> List:
        grouping = kwargs.get('grouping')
        kwargs['terms'] = terms
        if grouping is None:
            grouping = 'year'
            kwargs['grouping'] = grouping
        queries = self.build_queries(
            kwargs,
            queriesWithCounts
        )
        record_generator = self.fetch_from_queries(
            queries=queries,
            parser=self.solo_record_parser if grouping == 'all' else self.group_record_parser,
            onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)

    def build_queries(self, kwargs, queries_with_counts):
        if queries_with_counts:
            return self.queryBuilder.index_queries_by_num_results(queries_with_counts)
        else:
            return self.queryBuilder.build_queries_for_args(kwargs)

    def get_num_results_for_args(self, args):
        base_queries = self.queryBuilder.build_base_queries(args)
        return self.queryBuilder.get_num_results_for_query(base_queries)


class IssuesWrapper(GallicaWrapper):

    def post_init(self, kwargs):
        self.parser = buildParser('ark')

    def get_query_builder(self):
        return PaperQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/services/Issues'

    def get(self, codes, generate=False):
        queries = self.queryBuilder.build_ark_queries_for_codes(codes)
        record_generator = self.fetch_from_queries(
            queries,
            parser=self.parser
        )
        return record_generator if generate else list(record_generator)


class ContentWrapper(GallicaWrapper):

    def post_init(self, kwargs):
        self.parser = buildParser('content')

    def get_query_builder(self):
        return ContentQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/services/ContentSearch'

    def get(self, ark, term, generate=False):
        query = self.queryBuilder.build_query_for_ark_and_term(
            ark=ark,
            term=term
        )
        record_generator = self.fetch_from_queries(
            queries=query,
            parser=self.parser
        )
        return record_generator if generate else list(record_generator)


class PapersWrapper(GallicaWrapper):

    def post_init(self, kwargs):
        self.parser = buildParser('paper')
        self.issues_wrapper = IssuesWrapper()

    def get_query_builder(self):
        return PaperQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, argCodes, stateHooks=None, **kwargs):
        queries = self.queryBuilder.build_queries_for_args(argCodes)
        record_generator = self.fetch_from_queries(
            queries,
            parser=self.parser,
        )
        sru_paper_records = list(record_generator)
        codes = [record.code for record in sru_paper_records]
        year_records = self.issues_wrapper.get(codes)
        years_as_dict = {record.code: record.years for record in year_records}
        for record in sru_paper_records:
            record.addYearsFromArk(years_as_dict[record.code])
        return sru_paper_records


class FullTextWrapper(GallicaWrapper):

    def post_init(self, kwargs):
        self.parser = buildParser('fullText')

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr'

    def get_query_builder(self):
        return FullTextQueryBuilder(props=self)

    def get(self, ark_codes, generate=False):
        queries = self.queryBuilder.build_queries_for_ark_codes(ark_codes)
        record_generator = self.fetch_from_queries(
            queries=queries,
            parser=self.parser
        )
        return record_generator if generate else list(record_generator)
