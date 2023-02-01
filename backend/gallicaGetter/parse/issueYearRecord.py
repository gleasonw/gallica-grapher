from dataclasses import dataclass
from typing import List
from parse.parseXML import get_years_published
from  fetch.gallicasession import Response


def parse_responses_to_records(responses: List[Response], on_get_total_records):
    for response in responses:
        years = get_years_published(response.xml)
        code = response.query.get_code()
        yield IssueYearRecord(code=code, years=years)


@dataclass
class IssueYearRecord:
    code: str
    years: List[str]
