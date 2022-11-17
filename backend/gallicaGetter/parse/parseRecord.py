from gallicaGetter.parse.arkRecord import ArkRecord
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.gallicaxmlparse import GallicaXMLparse
from gallicaGetter.parse.groupedCountRecord import GroupedCountRecord
from gallicaGetter.parse.occurrenceRecord import OccurrenceRecord
from gallicaGetter.parse.paperRecord import PaperRecord
from gallicaGetter.parse.parseHTML import parse_html
from gallicaGetter.parse.contentRecord import ContentRecord


#TODO: refactor records into PeriodCount and VolumeOccurrence
def buildParser(desiredRecord, **kwargs):
    recordParsers = {
        'ark': ParseArkRecord,
        'groupedCount': ParseGroupedRecordCounts,
        'occurrence': ParseOccurrenceRecords,
        'paper': ParsePaperRecords,
        'content': ParseContentRecord,
        'fullText': ParseFullText,
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
            yield from self.generatePaperRecords(response.data)

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
                xml=response.data
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
            count = self.parser.getNumRecords(response.data)
            query = response.query
            yield GroupedCountRecord(
                date=Date(query.get_start_date()),
                count=count,
                ticketID=self.ticketID,
                term=query.term,
                requestID=self.requestID
            )


class ParseContentRecord(ParseRecord):

    def parseResponsesToRecords(self, responses):
        for response in responses:
            num_results_and_pages = self.parser.getNumResultsAndPagesForOccurrenceInPeriodical(response.data)
            yield ContentRecord(
                num_results=num_results_and_pages[0],
                pages=num_results_and_pages[1]
            )


class ParseFullText(ParseRecord):

    def parseResponsesToRecords(self, responses):
        return (
            parse_html(response.data)
            for response in responses
        )


class ParseArkRecord(ParseRecord):

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generateArkRecord(response.data, response.query)

    def generateArkRecord(self, xml, query):
        years = self.parser.getYearsPublished(xml)
        code = query.getCode()
        yield ArkRecord(
            code=code,
            years=years
        )
