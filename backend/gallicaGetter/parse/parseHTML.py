from bs4 import BeautifulSoup
from dataclasses import dataclass


def parse_html(html):
    return ParsedGallicaHTML(html)


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
