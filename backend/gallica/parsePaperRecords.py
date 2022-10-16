from paperRecord import PaperRecord


class ParsePaperRecords:

    def __init__(self, parser):
        self.parser = parser

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
