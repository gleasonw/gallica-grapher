from typing import Generator, List, Tuple
from pydantic import BaseModel
from gallicaGetter.parse_xml import get_num_results_and_pages_for_context
from gallicaGetter.gallicaWrapper import GallicaWrapper
from dataclasses import dataclass


class GallicaPage(BaseModel):
    page: str
    context: str


class GallicaContext(BaseModel):
    num_results: int
    pages: List[GallicaPage]
    ark: str


class ContextWrapper(GallicaWrapper):
    """Wrapper for Gallica's ContentSearch API."""

    def parse(self, gallica_responses):
        for response in gallica_responses:
            num_results_and_pages = get_num_results_and_pages_for_context(response.xml)
            yield GallicaContext(
                num_results=num_results_and_pages[0],
                pages=[
                    GallicaPage(page=occurrence[0], context=occurrence[1])
                    for occurrence in num_results_and_pages[1]
                ],
                ark=response.query.ark,
            )

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/services/ContentSearch"

    def get(
        self, context_pairs: List[Tuple[str, str]], generate=False
    ) -> Generator[GallicaContext, None, None]:
        queries = [
            ContentQuery(ark=pair[0], term=pair[1], endpoint_url=self.endpoint_url)
            for pair in context_pairs
        ]
        record_generator = self.get_records_for_queries(queries=queries)
        return record_generator


@dataclass(frozen=True, slots=True)
class ContentQuery:
    """Struct for query to Gallica's ContentSearch API."""

    ark: str
    term: str
    endpoint_url: str

    def get_params_for_fetch(self):
        return {"ark": self.ark, "query": self.term}
