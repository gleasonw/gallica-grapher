from typing import Callable, Generator, List, Literal, Optional, Tuple

from database.contextPair import ContextPair

from .buildqueries.argToQueryTransformations import (
    build_indexed_queries,
    get_num_results_for_queries,
    index_queries_by_num_results,
)
from .buildqueries.buildContentQuery import build_query_for_ark_and_term
from .buildqueries.buildIssueQueries import build_issue_queries_for_codes
from .buildqueries.buildPaperQueries import build_paper_queries_for_codes
from .buildqueries.buildSRUqueries import (
    build_base_queries,
    build_base_queries_at_indices,
)
from .buildqueries.buildTextQueries import build_text_queries_for_codes
from .parse.contentRecord import GallicaContext
from .parse.issueYearRecord import IssueYearRecord
from .parse.paperRecords import PaperRecord
from .parse.periodRecords import PeriodRecord
from .parse.volumeRecords import VolumeRecord
from .parse import (
    fullText,
    paperRecords,
    periodRecords,
    volumeRecords,
    issueYearRecord,
    contentRecord,
)


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

    def fetch_from_queries(
        self,
        queries,
        onUpdateProgress=None,
        on_get_total_records: Optional[Callable[[int], None]] = None,
    ):
        raw_response = self.api.get(
            queries,
            onProgressUpdate=onUpdateProgress,
        )
        return self.parser(raw_response, on_get_total_records=on_get_total_records)

    def get_parser(self):
        raise NotImplementedError(
            f"get_parser() not implemented for {self.__class__.__name__}"
        )

    def post_init(self):
        pass


class VolumeOccurrenceWrapper(GallicaWrapper):
    def get_parser(self):
        return volumeRecords.parse_responses_to_records

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def get(
        self,
        terms: List[str],
        source: Optional[Literal["book", "periodical", "all"]] = "all",
        link: Optional[Tuple[str, int]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        codes: Optional[List[str]] = None,
        num_results: Optional[int] = None,
        start_index: Optional[int] = 0,
        sort: Optional[Literal["date", "relevance"]] = None,
        onProgressUpdate=None,
        query_cache=None,
        on_get_total_records: Optional[Callable[[int], None]] = None,
    ) -> Generator[VolumeRecord, None, None]:
        if query_cache:
            queries = index_queries_by_num_results(query_cache)
        else:
            base_queries = build_base_queries(
                terms=terms,
                start_date=start_date,
                end_date=end_date,
                codes=codes,
                link=link,
                source=source,
                sort=sort,
                endpoint_url=self.endpoint_url,
                grouping="all",
                limit=num_results,
                cursor=start_index,
            )
            if isinstance(start_index, list):
                queries = build_base_queries_at_indices(
                    base_queries,
                    start_index,
                )
            elif num_results is None or num_results > 50:
                # assume we want all results, or index for more than 50
                # we will have to fetch # total records from Gallica
                queries = build_indexed_queries(
                    base_queries,
                    api=self.api,
                    limit=num_results,
                    offset=start_index,
                )
            else:
                # num results less than 50, the base query is fine
                queries = base_queries
        record_generator = self.fetch_from_queries(
            queries=queries,
            onUpdateProgress=onProgressUpdate,
            on_get_total_records=on_get_total_records,
        )
        return record_generator

    def get_num_results_for_args(
        self,
        terms: List[str],
        link: Optional[Tuple[str, int]],
        source: Optional[Literal["book", "periodical", "all"]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        codes: Optional[List[str]] = None,
        grouping: str = "all",
    ):
        base_queries = build_base_queries(
            terms=terms,
            start_date=start_date,
            end_date=end_date,
            codes=codes,
            link=link,
            source=source,
            endpoint_url=self.endpoint_url,
            grouping=grouping,
        )
        return get_num_results_for_queries(base_queries, api=self.api)


class PeriodOccurrenceWrapper(GallicaWrapper):
    def get(
        self,
        terms: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        codes: Optional[List[str]] = None,
        grouping: str = "year",
        onProgressUpdate=None,
    ) -> Generator[PeriodRecord, None, None]:
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
        return record_generator

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def get_parser(self):
        return periodRecords.parse_responses_to_records


class IssuesWrapper(GallicaWrapper):
    def get_parser(self):
        return issueYearRecord.parse_responses_to_records

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/services/Issues"

    def get(self, codes, generate=False) -> List[IssueYearRecord]:
        queries = build_issue_queries_for_codes(codes, endpoint_url=self.endpoint_url)
        record_generator = self.fetch_from_queries(queries)
        return record_generator if generate else list(record_generator)


class ContentWrapper(GallicaWrapper):
    def get_parser(self):
        return contentRecord.parse_responses_to_records

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/services/ContentSearch"

    def get(
        self, context_pairs: List[ContextPair], generate=False
    ) -> Generator[GallicaContext, None, None]:
        queries = [
            build_query_for_ark_and_term(
                ark=pair.ark_code, term=pair.term, endpoint_url=self.endpoint_url
            )
            for pair in context_pairs
        ]
        record_generator = self.fetch_from_queries(queries=queries)
        return record_generator


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
        return paperRecords.parse_responses_to_records


class FullTextWrapper(GallicaWrapper):
    def get_endpoint_url(self):
        return "https://gallica.bnf.fr"

    def get_parser(self):
        return fullText.parse_responses_to_records

    def get(
        self, ark_codes, onUpdateProgress=None, generate=False
    ) -> List[GallicaContext]:
        queries = build_text_queries_for_codes(
            endpoint=self.endpoint_url, ark_codes=ark_codes
        )
        record_generator = self.fetch_from_queries(
            queries=queries, onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)
