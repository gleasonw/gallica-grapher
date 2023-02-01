from dataclasses import dataclass
from typing import Callable, Optional

from parse.date import Date
from parse.parseXML import (
    get_records_from_xml,
    get_paper_title_from_record_xml,
    get_paper_code_from_record_xml,
    get_date_from_record_xml,
    get_url_from_record,
    get_num_records,
)


def parse_responses_to_records(
    responses, on_get_total_records: Optional[Callable[[int], None]] = None
):
    for response in responses:
        for i, record in enumerate(get_records_from_xml(response.xml)):
            if on_get_total_records and i == 0:
                on_get_total_records(get_num_records(response.xml))
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
