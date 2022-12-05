from bs4 import BeautifulSoup
from dataclasses import dataclass


def parse_html(html):
    return ParsedGallicaHTML(html)


@dataclass
class ParsedGallicaHTML(slots=True):
    html: str
    text: str = None
    ocr_quality: int = None

    def __post_init__(self):
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def get_text(self) -> str:
        if not self.text:
            hr_break_before_paras = self.soup.find('hr')
            if hr_break_before_paras:
                item_paras = hr_break_before_paras.find_next_siblings('p')
                self.text = '\n'.join([para.text for para in item_paras])
        return self.text

    def get_ocr_quality(self) -> int:
        if self.ocr_quality is None:
            ocrPara = self.soup.find('hr').find_previous_sibling('p').text
            if ocrPara[-6:-3].isdigit():
                self.ocr_quality = int(ocrPara[-6:-3])
            elif ocrPara[-5:-3].isdigit():
                self.ocr_quality = int(ocrPara[-5:-3])
            elif ocrPara[-4:-3].isdigit():
                self.ocr_quality = int(ocrPara[-4:-3])
            else:
                self.ocr_quality = 0
        return self.ocr_quality
