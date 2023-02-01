from dataclasses import dataclass
from typing import List
from gallicaGetter.parse.parseXML import (
    get_records_from_xml,
    get_paper_code_from_record_xml,
    get_paper_title_from_record_xml,
    get_url_from_record,
)


def parse_responses_to_records(responses, on_get_total_records):
    for response in responses:
        for record in get_records_from_xml(response.xml):
            yield PaperRecord(
                code=get_paper_code_from_record_xml(record),
                title=get_paper_title_from_record_xml(record),
                url=get_url_from_record(record),
                publishing_years=[],
            )


@dataclass(slots=True)
class PaperRecord:
    code: str
    title: str
    url: str
    publishing_years: List[int]

    @property
    def continuous(self):
        if self.publishing_years:
            return int(self.publishing_years[-1]) - int(
                self.publishing_years[0]
            ) + 1 == len(self.publishing_years)
        else:
            return False
