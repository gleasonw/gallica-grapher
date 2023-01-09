from typing import List, Optional

from gallicaGetter.buildqueries.argToQueryTransformations import (
    build_indexed_queries,
    get_num_results_for_queries,
    index_queries_by_num_results,
)
from gallicaGetter.buildqueries.buildContentQuery import build_query_for_ark_and_term
from gallicaGetter.buildqueries.buildIssueQueries import build_issue_queries_for_codes
from gallicaGetter.buildqueries.buildPaperQueries import build_paper_queries_for_codes
from gallicaGetter.buildqueries.buildSRUqueries import (
    build_base_queries,
    build_base_queries_at_indices,
)
from gallicaGetter.buildqueries.buildTextQueries import build_text_queries_for_codes
from gallicaGetter.parse import build_parser
from gallicaGetter.parse.contentRecord import ContentRecord
from gallicaGetter.parse.issueYearRecord import IssueYearRecord
from gallicaGetter.parse.paperRecords import PaperRecord
from gallicaGetter.parse.periodRecords import PeriodRecord
from gallicaGetter.parse.volumeRecords import VolumeRecord


class GallicaWrapper:
    def __init__(self, api):
        self.api = api
        self.endpoint_url = self.get_endpoint_url()
        self.parser = self.get_parser()
        self.post_init()

    def get(self, **kwargs):
        raise NotImplementedError(
            f"get() not implemented for {self.__class__.__name__}"
        )

    def get_endpoint_url(self):
        raise NotImplementedError(
            f"get_endpoint_url() not implemented for {self.__class__.__name__}"
        )

    def fetch_from_queries(self, queries, onUpdateProgress=None):
        raw_response = self.api.get(queries, onProgressUpdate=onUpdateProgress)
        return self.parser(raw_response)

    def get_parser(self):
        raise NotImplementedError(
            f"get_parser() not implemented for {self.__class__.__name__}"
        )

    def post_init(self):
        pass


class VolumeOccurrenceWrapper(GallicaWrapper):
    def get_parser(self):
        return build_parser("occurrence")

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def get(
        self,
        terms: List[str] | str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        codes: Optional[List[str] | str] = None,
        generate: bool = False,
        num_results: Optional[int] = None,
        start_index: Optional[int] = 0,
        num_workers: Optional[int] = 15,
        link_term: Optional[str] = None,
        link_distance: Optional[int] = None,
        onProgressUpdate=None,
        query_cache=None,
    ) -> List[VolumeRecord]:
        if query_cache:
            queries = index_queries_by_num_results(query_cache)
        else:
            base_queries = build_base_queries(
                terms=terms,
                start_date=start_date,
                end_date=end_date,
                codes=codes,
                link_term=link_term,
                link_distance=link_distance,
                endpoint_url=self.endpoint_url,
                grouping="all",
            )
            if isinstance(start_index, list):
                queries = build_base_queries_at_indices(
                    base_queries,
                    start_index,
                )
            else:
                queries = build_indexed_queries(
                    base_queries,
                    api=self.api,
                    limit=num_results,
                    offset=start_index,
                )
        record_generator = self.fetch_from_queries(
            queries=queries, onUpdateProgress=onProgressUpdate
        )
        return record_generator if generate else list(record_generator)

    def get_num_results_for_args(
        self,
        terms: List[str] | str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        codes: Optional[List[str] | str] = None,
        link_term: Optional[str] = None,
        link_distance: Optional[int] = None,
        grouping: str = "all",
    ):
        base_queries = build_base_queries(
            terms=terms,
            start_date=start_date,
            end_date=end_date,
            codes=codes,
            link_term=link_term,
            link_distance=link_distance,
            endpoint_url=self.endpoint_url,
            grouping=grouping,
        )
        return get_num_results_for_queries(base_queries, api=self.api)


class PeriodOccurrenceWrapper(GallicaWrapper):
    def get(
        self,
        terms: List[str] | str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        codes: Optional[List[str] | str] = None,
        generate: bool = False,
        num_results: Optional[int] = None,
        grouping: str = "year",
        start_index: Optional[int] = 0,
        num_workers: Optional[int] = 15,
        onProgressUpdate=None,
    ) -> List[PeriodRecord]:
        if grouping not in ["year", "month"]:
            raise ValueError(
                f'grouping must be either "year" or "month", not {grouping}'
            )
        queries = build_base_queries(
            terms=terms,
            start_date=start_date,
            end_date=end_date,
            codes=codes,
            endpoint_url=self.endpoint_url,
            grouping=grouping,
        )
        record_generator = self.fetch_from_queries(
            queries=queries, onUpdateProgress=onProgressUpdate
        )
        return record_generator if generate else list(record_generator)

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def get_parser(self):
        return build_parser("groupedCount")


class IssuesWrapper(GallicaWrapper):
    def get_parser(self):
        return build_parser("issues")

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/services/Issues"

    def get(self, codes, generate=False) -> List[IssueYearRecord]:
        queries = build_issue_queries_for_codes(codes, endpoint_url=self.endpoint_url)
        record_generator = self.fetch_from_queries(queries)
        return record_generator if generate else list(record_generator)


class ContentWrapper(GallicaWrapper):
    def get_parser(self):
        return build_parser("content")

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/services/ContentSearch"

    def get(self, ark, term, generate=False) -> List[ContentRecord]:
        query = build_query_for_ark_and_term(
            ark=ark, term=term, endpoint_url=self.endpoint_url
        )
        record_generator = self.fetch_from_queries(queries=query)
        return record_generator if generate else list(record_generator)


class PapersWrapper(GallicaWrapper):
    def post_init(self):
        self.issues_wrapper = IssuesWrapper(api=self.api)

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def get(self, arg_codes, stateHooks=None, **kwargs) -> List[PaperRecord]:
        queries = build_paper_queries_for_codes(
            arg_codes, endpoint_url=self.endpoint_url, api=self.api
        )
        record_generator = self.fetch_from_queries(queries)
        sru_paper_records = list(record_generator)
        codes = [record.code for record in sru_paper_records]
        year_records = self.issues_wrapper.get(codes)
        years_as_dict = {record.code: record.years for record in year_records}
        for record in sru_paper_records:
            record.publishing_years = years_as_dict[record.code]
        return sru_paper_records

    def get_parser(self):
        return build_parser("paper")


class FullTextWrapper(GallicaWrapper):
    def get_endpoint_url(self):
        return "https://gallica.bnf.fr"

    def get_parser(self):
        return build_parser("fullText")

    def get(
        self, ark_codes, onUpdateProgress=None, generate=False
    ) -> List[ContentRecord]:
        queries = build_text_queries_for_codes(
            endpoint=self.endpoint_url, ark_codes=ark_codes
        )
        record_generator = self.fetch_from_queries(
            queries=queries, onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)
