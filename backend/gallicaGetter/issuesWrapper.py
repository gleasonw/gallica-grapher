from typing import Generator, List
from gallicaGetter.queries import IssuesQuery
from gallicaGetter.utils.parse_xml import get_years_published
from gallicaGetter.gallicaWrapper import GallicaWrapper
from dataclasses import dataclass


@dataclass
class IssueYearRecord:
    code: str
    years: List[str]


class IssuesWrapper(GallicaWrapper):
    """Fetches periodical periodical publishing years from Gallica's Issues API. Used in PapersWrapper."""

    def parse(self, gallica_responses):
        for response in gallica_responses:
            years = get_years_published(response.xml)
            code = response.query.get_code()
            yield IssueYearRecord(code=code, years=years)

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/services/Issues"

    async def get(self, codes) -> Generator[IssueYearRecord, None, None]:
        if type(codes) == str:
            codes = [codes]
        queries = [
            IssuesQuery(code=code, endpoint_url=self.endpoint_url) for code in codes
        ]
        return await self.get_records_for_queries(queries)

