from typing import Generator, List
from gallicaGetter.parse_xml import get_years_published
from gallicaGetter.gallicaWrapper import GallicaWrapper
from dataclasses import dataclass


@dataclass
class IssueYearRecord:
    code: str
    years: List[str]


class IssuesWrapper(GallicaWrapper):
    def parse(self, gallica_responses, on_get_total_records):
        for response in gallica_responses:
            years = get_years_published(response.xml)
            code = response.query.get_code()
            yield IssueYearRecord(code=code, years=years)

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/services/Issues"

    def get(self, codes) -> Generator[IssueYearRecord, None, None]:
        if type(codes) == str:
            codes = [codes]
        queries = [
            IssuesQuery(code=code, endpoint_url=self.endpoint_url) for code in codes
        ]
        record_generator = self.get_records_for_queries(queries)
        return record_generator


class IssuesQuery:
    def __init__(self, code: str, endpoint_url: str):
        self.code = code
        self.endpoint_url = endpoint_url

    def get_code(self):
        return self.code

    def get_params_for_fetch(self):
        return {"ark": f"ark:/12148/{self.code}/date"}

    def __repr__(self):
        return f"ArkQuery({self.code})"
