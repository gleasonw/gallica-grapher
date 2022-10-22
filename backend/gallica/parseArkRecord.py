from gallica.dto.arkRecord import ArkRecord
from gallica.gallicaxmlparse import GallicaXMLparse


class ParseArkRecord:

    def __init__(self):
        self.parser = GallicaXMLparse()

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generateArkRecord(response.xml, response.query)

    def generateArkRecord(self, xml, query):
        years = self.parser.getYearsPublished(xml)
        code = query.getCode()
        yield ArkRecord(
            code=code,
            years=years
        )
