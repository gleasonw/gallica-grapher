from dataclasses import dataclass
from typing import Generator, List

from bs4 import BeautifulSoup
from gallicaGetter.gallicaWrapper import GallicaWrapper


@dataclass(slots=True)
class ParsedGallicaHTML:
    html: str
    soup: BeautifulSoup | None = None
    text: str = ""

    def __post_init__(self):
        self.soup = BeautifulSoup(markup=self.html, features="html.parser")

    @property
    def parsed_text(self) -> str:
        if self.soup:
            hr_break_before_paras = self.soup.find("hr")
            if hr_break_before_paras:
                item_paras = hr_break_before_paras.find_next_siblings("p")
                self.text = "\n".join([para.text for para in item_paras])
        return self.text


class FullTextWrapper(GallicaWrapper):
    def get_endpoint_url(self):
        return "https://gallica.bnf.fr"

    def parse(self, gallica_responses, on_get_total_records):
        return (ParsedGallicaHTML(response.xml) for response in gallica_responses)

    def get(
        self, ark_codes, onUpdateProgress=None
    ) -> Generator[ParsedGallicaHTML, None, None]:
        if type(ark_codes) is not list:
            ark_codes = [ark_codes]
        queries = [FullTextQuery(ark=code) for code in ark_codes]
        record_generator = self.get_records_for_queries(
            queries=queries, onUpdateProgress=onUpdateProgress
        )
        return record_generator


class FullTextQuery:
    def __init__(self, ark: str):
        self.ark = ark

    def get_params_for_fetch(self):
        return {}

    @property
    def endpoint_url(self):
        return f"https://gallica.bnf.fr/ark:/12148/{self.ark}.texteBrut"

    def __repr__(self) -> str:
        return f"RawTextQuery({self.ark})"
