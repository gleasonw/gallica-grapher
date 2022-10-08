from lxml import etree
from gallica.dto.occurrenceRecord import OccurrenceRecord


class ParseOccurrenceRecords:

    def __init__(self, parser):
        self.parser = parser

    def generateOccurrenceRecords(self, xml):
        elements = etree.fromstring(xml)
        if elements.find("{http://www.loc.gov/zing/srw/}records") is None:
            return []
        for record in elements.iter("{http://www.loc.gov/zing/srw/}record"):
            data = self.parser.getDataFromRecordRoot(record)
            paperTitle = self.parser.getPaperTitle(data)
            paperCode = self.parser.getPaperCode(data)
            date = self.parser.getDate(data)
            newRecord = OccurrenceRecord(
                paperTitle=paperTitle,
                paperCode=paperCode,
                date=date,
                url=self.parser.getURL(data),
            )
            yield newRecord
