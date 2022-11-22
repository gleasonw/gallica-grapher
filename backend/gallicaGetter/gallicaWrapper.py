from gallicaGetter.buildqueries.argToQueryTransformations import get_num_results_for_query
from gallicaGetter.buildqueries.buildSRUqueries import build_queries
from gallicaGetter.buildqueries.buildPaperQueries import build_paper_queries_for_codes
from gallicaGetter.buildqueries.buildTextQueries import build_text_queries_for_codes
from gallicaGetter.buildqueries.buildContentQuery import build_query_for_ark_and_term
from gallicaGetter.buildqueries.buildIssueQueries import build_issue_queries_for_codes
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
        self.post_init(kwargs)

    def post_init(self, kwargs):
        pass

    def get(self, **kwargs):
        raise NotImplementedError(f'get() not implemented for {self.__class__.__name__}')

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

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, terms, onUpdateProgress=None,
            generate=False, query_cache=None, **kwargs) -> List[VolumeOccurrenceRecord]:
        kwargs['terms'] = terms
        queries = build_queries(
            args=kwargs,
            endpoint_url=self.endpoint_url,
            query_cache=query_cache
        )
        record_generator = self.fetch_from_queries(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)

    def get_num_results_for_args(self, **kwargs):
        base_queries = build_queries(
            args=kwargs,
            endpoint_url=self.endpoint_url
        )
        return get_num_results_for_query(base_queries, api=self.api)


class PeriodOccurrenceWrapper(GallicaWrapper):

    def get(self, terms, onUpdateProgress=None, generate=False, **kwargs) -> List[PeriodOccurrenceRecord]:
        kwargs['terms'] = terms
        kwargs['grouping'] = 'period'
        queries = build_queries(kwargs, endpoint_url=self.endpoint_url)
        record_generator = self.fetch_from_queries(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)

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

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/services/Issues'

    def get(self, codes, generate=False) -> List[ArkRecord]:
        queries = build_issue_queries_for_codes(codes, endpoint_url=self.endpoint_url)
        record_generator = self.fetch_from_queries(queries)
        return record_generator if generate else list(record_generator)


class ContentWrapper(GallicaWrapper):

    def get_parser(self, kwargs):
        return buildParser('content')

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/services/ContentSearch'

    def get(self, ark, term, generate=False) -> List[ContentRecord]:
        query = build_query_for_ark_and_term(
            ark=ark,
            term=term,
            endpoint_url=self.endpoint_url
        )
        record_generator = self.fetch_from_queries(queries=query)
        return record_generator if generate else list(record_generator)


class PapersWrapper(GallicaWrapper):

    def post_init(self, kwargs):
        self.issues_wrapper = IssuesWrapper()

    def get_endpoint_url(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, arg_codes, stateHooks=None, **kwargs) -> List[PaperRecord]:
        queries = build_paper_queries_for_codes(arg_codes)
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

    def get_parser(self, kwargs):
        return buildParser('fullText')

    def get(self, ark_codes, onUpdateProgress=None, generate=False) -> List[ContentRecord]:
        queries = build_text_queries_for_codes(ark_codes)
        record_generator = self.fetch_from_queries(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)
