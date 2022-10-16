from gallica.dto.occurrenceRecord import OccurrenceRecord


class ParseOccurrenceRecords:

    def __init__(self, parser, requestID, ticketID):
        self.parser = parser
        self.requestID = requestID
        self.ticketID = ticketID

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generateOccurrenceRecords(
                query=response.query,
                xml=response.xml
            )

    def generateOccurrenceRecords(self, xml, query):
        for record in self.parser.getRecordsFromXML(xml):
            paperTitle = self.parser.getPaperTitleFromRecord(record)
            paperCode = self.parser.getPaperCodeFromRecord(record)
            date = self.parser.getDateFromRecord(record)
            yield OccurrenceRecord(
                paperTitle=paperTitle,
                paperCode=paperCode,
                date=date,
                url=self.parser.getURLfromRecord(record),
                term=query.term,
                requestID=self.requestID,
                ticketID=self.ticketID
            )
