from typing import List, Tuple

from pydantic import BaseModel

from gallicaGetter.fetch.gallicasession import Response
from gallicaGetter.parse.parseXML import get_num_results_and_pages_for_context


def parse_responses_to_records(responses: List[Response]):
    for response in responses:
        num_results_and_pages = get_num_results_and_pages_for_context(response.xml)
        yield ContentRecord(
            num_results=num_results_and_pages[0], pages=num_results_and_pages[1]
        )


class ContentRecord(BaseModel):
    num_results: int
    pages: List[Tuple[str, str]]
