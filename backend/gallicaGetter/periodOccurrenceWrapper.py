from dataclasses import dataclass

import aiohttp
from gallicaGetter.utils.date import Date
from gallicaGetter.utils.parse_xml import get_num_records_from_gallica_xml
from gallicaGetter.gallicaWrapper import GallicaWrapper
from gallicaGetter.utils.base_query_builds import build_base_queries
from typing import Generator, List, Optional


@dataclass(slots=True)
class PeriodRecord:
    date: Date
    count: int
    term: str


class PeriodOccurrenceWrapper(GallicaWrapper):
    """Fetches # occurrences of terms in a given period of time. Useful for making graphs."""

    async def get(
        self,
        terms: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        codes: Optional[List[str]] = None,
        grouping: str = "year",
        onProgressUpdate=None,
        session: aiohttp.ClientSession | None = None,
    ) -> Generator[PeriodRecord, None, None]:
        if session is None:
            async with aiohttp.ClientSession() as session:
                return await self.get(
                    terms=terms,
                    start_date=start_date,
                    end_date=end_date,
                    codes=codes,
                    grouping=grouping,
                    onProgressUpdate=onProgressUpdate,
                    session=session,
                )
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
        return await self.get_records_for_queries(
            queries=queries, on_update_progress=onProgressUpdate, session=session
        )

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def parse(self, gallica_responses):
        for response in gallica_responses:
            count = get_num_records_from_gallica_xml(response.xml)
            query = response.query
            yield PeriodRecord(
                date=Date(query.start_date),
                count=count,
                term=query.terms,
            )
