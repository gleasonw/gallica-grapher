from typing import List

from pydantic import BaseModel

from ..fetch.gallicasession import Response
from ..parse.parseXML import get_num_results_and_pages_for_context


def parse_responses_to_records(responses: List[Response], on_get_total_records):
    for response in responses:
        num_results_and_pages = get_num_results_and_pages_for_context(response.xml)
        yield GallicaContext(
            num_results=num_results_and_pages[0],
            pages=[
                GallicaPage(page=occurrence[0], context=occurrence[1])
                for occurrence in num_results_and_pages[1]
            ],
            ark=response.query.ark,
        )


class GallicaPage(BaseModel):
    page: str
    context: str


class GallicaContext(BaseModel):
    num_results: int
    pages: List[GallicaPage]
    ark: str
