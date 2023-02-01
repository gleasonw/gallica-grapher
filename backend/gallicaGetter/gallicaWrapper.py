from typing import Callable, Generator, List, Literal, Optional, Tuple
from gallicaGetter.fetch.fullTextQuery import FullTextQuery
from gallicaGetter.buildqueries.buildDateGrouping import build_date_grouping
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery

from gallicaGetter.parse.parseHTML import ParsedGallicaHTML

from backend.contextPair import ContextPair

from gallicaGetter.buildqueries.argToQueryTransformations import (
    build_indexed_queries,
    bundle_codes,
    get_num_results_for_queries,
    index_queries_by_num_results,
)
from gallicaGetter.buildqueries.buildContentQuery import build_query_for_ark_and_term
from gallicaGetter.buildqueries.buildIssueQueries import build_issue_queries_for_codes
from gallicaGetter.buildqueries.buildPaperQueries import build_paper_queries_for_codes
from gallicaGetter.parse.contentRecord import GallicaContext
from gallicaGetter.parse.issueYearRecord import IssueYearRecord
from gallicaGetter.parse.paperRecords import PaperRecord
from gallicaGetter.parse.periodRecords import PeriodRecord
from gallicaGetter.parse.volumeRecords import VolumeRecord
from gallicaGetter.parse import (
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
        start_index: int | List[int] = 0,
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
            if num_results and num_results > 50:
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
        link: Optional[Tuple[str, int]] = None,
        source: Optional[Literal["book", "periodical", "all"]] = "all",
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
    ) -> List[ParsedGallicaHTML]:
        if type(ark_codes) is not list:
            ark_codes = [ark_codes]
        queries = [FullTextQuery(ark=code) for code in ark_codes]
        record_generator = self.fetch_from_queries(
            queries=queries, onUpdateProgress=onUpdateProgress
        )
        return record_generator if generate else list(record_generator)


def build_base_queries(
    terms: List[str],
    endpoint_url: str,
    grouping: str,
    link: Optional[Tuple[str, int]] = None,
    source: Optional[Literal["book", "periodical", "all"]] = None,
    sort: Optional[Literal["date", "relevance"]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    codes: Optional[List[str]] = None,
    limit: Optional[int] = None,
    cursor: int | List[int] = 0,
) -> List[OccurrenceQuery]:
    """
    Builds a list of queries to be used to fetch records from Gallica.
    If pulling all records for the query, this query will be used to get the number of records and then
    spawn additional indexed queries to fetch all records in batches of 50.
    """
    base_queries = []
    for term in terms:
        for start, end in build_date_grouping(start_date, end_date, grouping):
            for code_bundle in bundle_codes(codes):
                if type(cursor) is int:
                    cursor = [cursor]
                for c in cursor:  # type: ignore
                    base_queries.append(
                        OccurrenceQuery(
                            term=term,
                            codes=code_bundle,
                            start_date=start,
                            end_date=end,
                            endpoint_url=endpoint_url,
                            start_index=c,
                            num_records=limit or 1,
                            link=link,
                            source=source,
                            sort=sort,
                        )
                    )
    return base_queries
