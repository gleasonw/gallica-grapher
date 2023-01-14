from dataclasses import dataclass

from gallicaGetter.parse.date import Date
from gallicaGetter.parse.parseXML import (
    get_records_from_xml,
    get_paper_title_from_record_xml,
    get_paper_code_from_record_xml,
    get_date_from_record_xml,
    get_url_from_record,
)


def parse_responses_to_records(responses):
    for response in responses:
        for record in get_records_from_xml(response.xml):
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


@dataclass(frozen=True, slots=True)
class VolumeRecord:
    paper_title: str
    paper_code: str
    url: str
    date: Date
    term: str
