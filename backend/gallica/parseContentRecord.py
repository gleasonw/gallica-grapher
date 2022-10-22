from gallica.gallicaxmlparse import GallicaXMLparse


class ParseContentRecord:

    def __init__(self):
        self.parser = GallicaXMLparse()

    def parseResponsesToRecords(self, responses):
        return (
            self.parser.getNumResultsAndPagesForOccurrenceInPeriodical(response.xml)
            for response in responses
        )