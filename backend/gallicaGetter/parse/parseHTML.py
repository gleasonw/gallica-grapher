from bs4 import BeautifulSoup


def parse_html(htmlData):
    return ParsedGallicaHTML(htmlData)


class ParsedGallicaHTML:

    def __init__(self, htmlData):
        self.html = htmlData
        self.soup = BeautifulSoup(htmlData, 'html.parser')

    def __repr__(self):
        return f'ParsedGallicaHTML({self.soup.title.string})'

    def get_text(self) -> str:
        itemParas = self.soup.find('hr').find_next_siblings('p')
        text = '\n'.join([para.text for para in itemParas])
        return text

    def get_ocr_quality(self) -> int:
        ocrQuality = self.soup.find('hr').find_previous_sibling('p').text
        return int(ocrQuality[-4:-2])