from dataclasses import dataclass
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.parseXML import get_num_records
from typing import List
from gallicaGetter.fetch.gallicasession import Response


def parse_responses_to_records(responses: List[Response], on_get_total_records):
    for response in responses:
        count = get_num_records(response.xml)
        query = response.query
        yield PeriodRecord(
            date=Date(query.start_date),
            count=count,
            term=query.term,
        )


@dataclass(slots=True)
class PeriodRecord:
    date: Date
    count: int
    term: str
