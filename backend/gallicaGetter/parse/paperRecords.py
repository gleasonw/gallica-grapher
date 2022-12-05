from dataclasses import dataclass
from typing import Optional, List
from gallicaGetter.parse.parseXML import (
    get_records_from_xml,
    get_paper_code_from_record_xml,
    get_paper_title_from_record_xml,
    get_url_from_record
)


def parse_responses_to_records(responses):
    for response in responses:
        for record in get_records_from_xml(response.xml):
            yield PaperRecord(
                code=get_paper_code_from_record_xml(record),
                title=get_paper_title_from_record_xml(record),
                url=get_url_from_record(record)
            )


@dataclass
class PaperRecord:
    code: str
    title: str
    url: str
    publishingYears: Optional[List[int]] = None

    @property
    def continuous(self):
        if self.publishingYears:
            return int(self.publishingYears[-1]) - int(self.publishingYears[0]) + 1 == len(self.publishingYears)
        else:
            return False
