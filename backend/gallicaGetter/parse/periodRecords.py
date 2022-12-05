from dataclasses import dataclass
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.parseXML import get_num_records


def parse_responses_to_records(responses):
    for response in responses:
        count = get_num_records(response.data)
        query = response.query
        yield PeriodOccurrenceRecord(
            date=Date(query.start_date),
            count=count,
            term=query.term,
        )


@dataclass
class PeriodOccurrenceRecord(slots=True):
    date: Date
    count: int
    term: str
