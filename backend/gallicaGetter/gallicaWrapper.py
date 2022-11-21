import gallicaGetter.buildqueries as query_builder
from gallicaGetter.buildqueries.contentQueryBuilder import ContentQueryBuilder
from gallicaGetter.buildqueries.fullTextQueryBuilder import FullTextQueryBuilder
from gallicaGetter.parse.parseRecord import buildParser
from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from gallicaGetter.parse.record import (
    VolumeOccurrenceRecord,
    PaperRecord,
    PeriodOccurrenceRecord,
    ContentRecord,
    ArkRecord
)
from typing import List


# TODO: add graceful timeouts
class GallicaWrapper:
    def __init__(self, **kwargs):
        self.api = ConcurrentFetch(numWorkers=kwargs.get('numWorkers', 15))
        self.endpoint_url = self.get_endpoint_url()
        self.parser = self.get_parser(kwargs)
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

    def fetch_from_queries(self, queries, onUpdateProgress=None):
        raw_response = self.api.get(
            queries,
            onUpdateProgress=onUpdateProgress
        )
        records = self.parser.parseResponsesToRecords(raw_response)
        return records

    def get_parser(self, kwargs):
        raise NotImplementedError(f'getParser() not implemented for {self.__class__.__name__}')


class VolumeOccurrenceWrapper(GallicaWrapper):

    def get_parser(self, kwargs):
        return buildParser(
            desiredRecord='occurrence',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )

    def get_query_builder(self):
        return OccurrenceQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, terms, onUpdateProgress=None,
            generate=False, queries_with_counts=None, **kwargs) -> List[VolumeOccurrenceRecord]:
        kwargs['terms'] = terms
        kwargs['grouping'] = 'all'
        queries = self.build_queries(
            kwargs,
            queries_with_counts
        )
        record_generator = self.fetch_from_queries(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)

    def build_queries(self, kwargs, queries_with_counts):
        if queries_with_counts:
            return self.queryBuilder.index_queries_by_num_results(queries_with_counts)
        else:
            return self.queryBuilder.build_queries_for_args(kwargs)

    def get_num_results_for_args(self, **kwargs):
        base_queries = self.queryBuilder.build_base_queries(kwargs)
        return self.queryBuilder.get_num_results_for_query(base_queries)


class PeriodOccurrenceWrapper(GallicaWrapper):

    def get(self, terms, onUpdateProgress=None, generate=False, **kwargs) -> List[PeriodOccurrenceRecord]:
        kwargs['terms'] = terms
        kwargs['grouping'] = 'period'
        queries = self.queryBuilder.build_queries_for_args(kwargs)
        record_generator = self.fetch_from_queries(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)

    def get_query_builder(self):
        return OccurrenceQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/SRU'

    def get_parser(self, kwargs):
        self.parser = buildParser(
            desiredRecord='groupedCount',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )


class IssuesWrapper(GallicaWrapper):

    def get_parser(self, kwargs):
        return buildParser('ark')

    def get_query_builder(self):
        return PaperQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/services/Issues'

    def get(self, codes, generate=False) -> List[ArkRecord]:
        queries = self.queryBuilder.build_ark_queries_for_codes(codes)
        record_generator = self.fetch_from_queries(queries)
        return record_generator if generate else list(record_generator)


class ContentWrapper(GallicaWrapper):

    def get_parser(self, kwargs):
        return buildParser('content')

    def get_query_builder(self):
        return ContentQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/services/ContentSearch'

    def get(self, ark, term, generate=False) -> List[ContentRecord]:
        query = self.queryBuilder.build_query_for_ark_and_term(
            ark=ark,
            term=term
        )
        record_generator = self.fetch_from_queries(queries=query)
        return record_generator if generate else list(record_generator)


class PapersWrapper(GallicaWrapper):

    def post_init(self, kwargs):
        self.issues_wrapper = IssuesWrapper()

    def get_query_builder(self):
        return PaperQueryBuilder(props=self)

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, arg_codes, stateHooks=None, **kwargs) -> List[PaperRecord]:
        queries = self.queryBuilder.build_queries_for_args(arg_codes)
        record_generator = self.fetch_from_queries(queries)
        sru_paper_records = list(record_generator)
        codes = [record.code for record in sru_paper_records]
        year_records = self.issues_wrapper.get(codes)
        years_as_dict = {record.code: record.years for record in year_records}
        for record in sru_paper_records:
            record.addYearsFromArk(years_as_dict[record.code])
        return sru_paper_records

    def get_parser(self, kwargs):
        return buildParser('paper')


class FullTextWrapper(GallicaWrapper):

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr'

    def get_query_builder(self):
        return FullTextQueryBuilder(props=self)

    def get_parser(self, kwargs):
        return buildParser('fullText')

    def get(self, ark_codes, onUpdateProgress=None, generate=False) -> List[ContentRecord]:
        queries = self.queryBuilder.build_queries_for_ark_codes(ark_codes)
        record_generator = self.fetch_from_queries(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)
