from dataclasses import dataclass

from gallicaGetter.base_query_builds import build_base_queries
from gallicaGetter.index_query_builds import (
    build_indexed_queries,
    get_num_results_for_queries,
    index_queries_by_num_results,
)
from gallicaGetter.date import Date
from gallicaGetter.gallicaWrapper import GallicaWrapper
from gallicaGetter.parse_xml import (
    get_records_from_xml,
    get_paper_title_from_record_xml,
    get_paper_code_from_record_xml,
    get_date_from_record_xml,
    get_url_from_record,
    get_num_records_from_gallica_xml,
)

from typing import Callable, Generator, List, Literal, Optional, Tuple


@dataclass(frozen=True, slots=True)
class VolumeRecord:
    paper_title: str
    paper_code: str
    url: str
    date: Date
    term: str


class VolumeOccurrenceWrapper(GallicaWrapper):
    """Fetches occurrence metadata from Gallica's SRU API. There may be many occurrences in one Gallica record."""

    def parse(
        self,
        gallica_responses,
    ):
        for response in gallica_responses:
            for i, record in enumerate(get_records_from_xml(response.xml)):
                if self.on_get_total_records and i == 0:
                    self.on_get_total_records(
                        get_num_records_from_gallica_xml(response.xml)
                    )
                paper_title = get_paper_title_from_record_xml(record)
                paper_code = get_paper_code_from_record_xml(record)
                date = get_date_from_record_xml(record)
                yield VolumeRecord(
                    paper_title=paper_title,
                    paper_code=paper_code,
                    date=date,
                    url=get_url_from_record(record),
                    term=response.query.term,
                )

    def post_init(self):
        self.on_get_total_records: Optional[Callable[[int], None]] = None

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
        get_all_results: bool = False,
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
            if (num_results and num_results > 50) or get_all_results:
                # assume we want all results, or index for more than 50
                # we will have to fetch # total records from Gallica
                queries = build_indexed_queries(
                    base_queries,
                    api=self.api,
                    limit=num_results,
                )
            else:
                # num results less than 50, the base query is fine
                queries = base_queries
        if on_get_total_records:
            # If we want to know the total number of records, we need to assign the callback
            self.on_get_total_records = on_get_total_records
        record_generator = self.get_records_for_queries(
            queries=queries,
            on_update_progress=onProgressUpdate,
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
        """Returns Gallica's knowledge of the number of records in the database that match the given arguments."""
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
