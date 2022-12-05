from dataclasses import dataclass
from typing import List

from gallicaGetter.parse.parseXML import get_years_published


def parse_responses_to_records(responses):
    for response in responses:
        years = get_years_published(response.data)
        code = response.query.get_code()
        yield ArkRecord(
            code=code,
            years=years
        )


@dataclass
class ArkRecord:
    code: str
    years: List[int]
