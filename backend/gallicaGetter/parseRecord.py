from gallicaGetter.arkRecord import ArkRecord
from gallicaGetter.date import Date
from gallicaGetter.gallicaxmlparse import GallicaXMLparse
from gallicaGetter.groupedCountRecord import GroupedCountRecord
from gallicaGetter.occurrenceRecord import OccurrenceRecord
from gallicaGetter.paperRecord import PaperRecord


def buildParser(desiredRecord, **kwargs):
    recordParsers = {
        'ark': ParseArkRecord,
        'groupedCount': ParseGroupedRecordCounts,
        'occurrence': ParseOccurrenceRecords,
        'paper': ParsePaperRecords,
        'content': ParseContentRecord
    }
    if desiredRecord not in recordParsers:
        raise ValueError(f'Unrecognized record type: {desiredRecord}. Options include: {recordParsers.keys()}')
    parser = GallicaXMLparse()
    return recordParsers[desiredRecord](parser, **kwargs)


class ParseRecord:

    def __init__(self, parser, **kwargs):
        self.parser = parser
        self.postInit(kwargs)

    def postInit(self, args):
        pass

    def parseResponsesToRecords(self, responses):
        raise NotImplementedError(f'ParseRecord.parseResponsesToRecords() must be implemented by subclass {self.__class__.__name__}.')


class ParsePaperRecords(ParseRecord):

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


class ParseOccurrenceRecords(ParseRecord):

    def postInit(self, args):
        self.requestID = args['requestID']
        self.ticketID = args['ticketID']

    def getNumResults(self, xml):
        return self.parser.getNumRecords(xml)

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


class ParseGroupedRecordCounts(ParseRecord):

    def postInit(self, args):
        self.ticketID = args['ticketID']
        self.requestID = args['requestID']

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


class ParseContentRecord(ParseRecord):

    def parseResponsesToRecords(self, responses):
        return (
            self.parser.getNumResultsAndPagesForOccurrenceInPeriodical(response.xml)
            for response in responses
        )


class ParseArkRecord(ParseRecord):

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
