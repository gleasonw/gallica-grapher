from paperRecord import PaperRecord
from gallicaxmlparse import GallicaXMLparse


class ParsePaperRecords:

    def __init__(self):
        self.parser = GallicaXMLparse()

    def getNumResults(self, xml):
        return self.parser.getNumRecords(xml)

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generatePaperRecords(response.xml)

    def generatePaperRecords(self, xml):
        for record in self.parser.getRecordsFromXML(xml):
            yield PaperRecord(
                code=self.parser.getPaperCodeFromRecord(record),
                title=self.parser.getPaperTitleFromRecord(record),
                url=self.parser.getURLfromRecord(record),
            )
