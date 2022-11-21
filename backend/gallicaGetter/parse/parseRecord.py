from gallicaGetter.parse.date import Date
from gallicaGetter.parse.gallicaxmlparse import GallicaXMLparse
from gallicaGetter.parse.record import VolumeOccurrenceRecord, PeriodOccurrenceRecord, PaperRecord, ContentRecord, \
    ArkRecord
from gallicaGetter.parse.parseHTML import parse_html


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
        return self.parser.get_num_records(xml)

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generatePaperRecords(response.data)

    def generatePaperRecords(self, xml):
        for record in self.parser.get_records_from_xml(xml):
            yield PaperRecord(
                code=self.parser.get_paper_code_from_record_xml(record),
                title=self.parser.get_paper_title_from_record_xml(record),
                url=self.parser.get_url_from_record(record),
            )


class ParseOccurrenceRecords(ParseRecord):

    def postInit(self, args):
        self.requestID = args['requestID']
        self.ticketID = args['ticketID']

    def getNumResults(self, xml):
        return self.parser.get_num_records(xml)

    def parseResponsesToRecords(self, responses):
        for response in responses:
            yield from self.generateOccurrenceRecords(
                query=response.query,
                xml=response.data
            )

    def generateOccurrenceRecords(self, xml, query):
        for record in self.parser.get_records_from_xml(xml):
            paperTitle = self.parser.get_paper_title_from_record_xml(record)
            paperCode = self.parser.get_paper_code_from_record_xml(record)
            date = self.parser.get_date_from_record_xml(record)
            yield VolumeOccurrenceRecord(
                paperTitle=paperTitle,
                paperCode=paperCode,
                date=date,
                url=self.parser.get_url_from_record(record),
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
            count = self.parser.get_num_records(response.data)
            query = response.query
            yield PeriodOccurrenceRecord(
                date=Date(query.get_start_date()),
                count=count,
                ticketID=self.ticketID,
                term=query.term,
                requestID=self.requestID
            )


class ParseContentRecord(ParseRecord):

    def parseResponsesToRecords(self, responses):
        for response in responses:
            num_results_and_pages = self.parser.get_num_results_and_pages_for_context(response.data)
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
        years = self.parser.get_years_published(xml)
        code = query.getCode()
        yield ArkRecord(
            code=code,
            years=years
        )
