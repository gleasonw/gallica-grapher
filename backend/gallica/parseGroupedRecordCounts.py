from gallica.date import Date
from gallica.dto.groupedCountRecord import GroupedCountRecord
from gallica.gallicaxmlparse import GallicaXMLparse


class ParseGroupedRecordCounts:

    def __init__(self, ticketID, requestID):
        self.parser = GallicaXMLparse()
        self.ticketID = ticketID
        self.requestID = requestID

    def parseResponsesToRecords(self, responses):
        for response in responses:
            count = self.parser.getNumRecords(response.xml)
            query = response.query
            yield GroupedCountRecord(
                date=Date(query.getStartDate()),
                count=count,
                ticketID=self.ticketID,
                term=query.term,
                requestID=self.requestID
            )
