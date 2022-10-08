from lxml import etree
from gallica.dto.paperRecord import PaperRecord


class ParsePaperRecords:

    def __init__(self, parser):
        self.parser = parser

    def generatePaperRecords(self, xml):
        elements = etree.fromstring(xml)
        if elements.find("{http://www.loc.gov/zing/srw/}records") is None:
            return []
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.parser.getDataFromRecordRoot(record)
            newRecord = PaperRecord(
                code=self.parser.getPaperCode(data),
                title=self.parser.getPaperTitle(data),
                url=self.parser.getURL(data),
            )
            yield newRecord