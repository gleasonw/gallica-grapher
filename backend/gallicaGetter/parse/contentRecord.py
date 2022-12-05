from dataclasses import dataclass
from typing import List, Tuple
from gallicaGetter.parse.parseXML import get_num_results_and_pages_for_context


def parse_responses_to_records(responses):
    for response in responses:
        num_results_and_pages = get_num_results_and_pages_for_context(response.data)
        yield ContentRecord(
            num_results=num_results_and_pages[0],
            pages=num_results_and_pages[1]
        )


@dataclass
class ContentRecord:
    num_results: int
    pages: List[Tuple[str, str]]
