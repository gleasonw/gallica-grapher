from dataclasses import dataclass
from gallicaGetter.date import Date
from gallicaGetter.parse_xml import get_num_records_from_gallica_xml
from gallicaGetter.gallicaWrapper import GallicaWrapper
from gallicaGetter.base_query_builds import build_base_queries
from typing import Generator, List, Optional


@dataclass(slots=True)
class PeriodRecord:
    date: Date
    count: int
    term: str


class PeriodOccurrenceWrapper(GallicaWrapper):
    """Fetches # occurrences of terms in a given period of time. Useful for making graphs."""

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
        record_generator = self.get_records_for_queries(
            queries=queries, on_update_progress=onProgressUpdate
        )
        return record_generator

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def parse(self, gallica_responses):
        for response in gallica_responses:
            count = get_num_records_from_gallica_xml(response.xml)
            query = response.query
            yield PeriodRecord(
                date=Date(query.start_date),
                count=count,
                term=query.term,
            )
