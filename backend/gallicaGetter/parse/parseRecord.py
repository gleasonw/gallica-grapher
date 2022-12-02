from gallicaGetter.parse.parseXML import (
    get_num_records,
    get_records_from_xml,
    get_paper_code_from_record_xml,
    get_paper_title_from_record_xml,
    get_url_from_record,
    get_date_from_record_xml,
    get_num_results_and_pages_for_context,
    get_years_published
)
from gallicaGetter.parse.arkRecord import ArkRecord
from gallicaGetter.parse.contentRecord import ContentRecord
from gallicaGetter.parse.paperRecord import PaperRecord
from gallicaGetter.parse.periodOccurrenceRecord import PeriodOccurrenceRecord
from gallicaGetter.parse.volumeOccurrenceRecord import VolumeOccurrenceRecord
from gallicaGetter.parse.parseHTML import parse_html
from gallicaGetter.parse.date import Date


def build_parser(desired_record, **kwargs):
    record_parsers = {
        'ark': ParseArkRecord,
        'groupedCount': ParseGroupedRecordCounts,
        'occurrence': ParseOccurrenceRecords,
        'paper': ParsePaperRecords,
        'content': ParseContentRecord,
        'fullText': ParseFullText,
    }
    if desired_record not in record_parsers:
        raise ValueError(f'Unrecognized record type: {desired_record}. Options include: {record_parsers.keys()}')
    return record_parsers[desired_record](**kwargs)


class ParseRecord:
    # Mixin to remind me to always add a parse_responses method

    def parse_responses_to_records(self, responses):
        raise NotImplementedError(f'parse_responses_to_records not implemented for {self.__class__.__name__}')


class ParsePaperRecords(ParseRecord):

    def get_num_results(self, xml):
        return get_num_records(xml)

    def parse_responses_to_records(self, responses):
        for response in responses:
            yield from self.generate_paper_records(response.data)

    def generate_paper_records(self, xml):
        for record in get_records_from_xml(xml):
            yield PaperRecord(
                code=get_paper_code_from_record_xml(record),
                title=get_paper_title_from_record_xml(record),
                url=get_url_from_record(record),
            )


class ParseOccurrenceRecords(ParseRecord):

    def __init__(self, requestID, ticketID):
        self.requestID = requestID
        self.ticketID = ticketID

    def get_num_results(self, xml):
        return get_num_records(xml)

    def parse_responses_to_records(self, responses):
        for response in responses:
            yield from self.generate_occurrence_records(
                query=response.query,
                xml=response.data
            )

    def generate_occurrence_records(self, xml, query):
        for record in get_records_from_xml(xml):
            paper_title = get_paper_title_from_record_xml(record)
            paper_code = get_paper_code_from_record_xml(record)
            date = get_date_from_record_xml(record)
            yield VolumeOccurrenceRecord(
                paper_title=paper_title,
                paper_code=paper_code,
                date=date,
                url=get_url_from_record(record),
                term=query.term,
                requestID=self.requestID,
                ticketID=self.ticketID
            )


class ParseGroupedRecordCounts(ParseRecord):

    def __init__(self, ticketID, requestID):
        self.ticketID = ticketID
        self.requestID = requestID

    def parse_responses_to_records(self, responses):
        for response in responses:
            count = get_num_records(response.data)
            query = response.query
            yield PeriodOccurrenceRecord(
                date=Date(query.start_date),
                count=count,
                ticketID=self.ticketID,
                term=query.term,
                requestID=self.requestID
            )


class ParseContentRecord(ParseRecord):

    def parse_responses_to_records(self, responses):
        for response in responses:
            num_results_and_pages = get_num_results_and_pages_for_context(response.data)
            yield ContentRecord(
                num_results=num_results_and_pages[0],
                pages=num_results_and_pages[1]
            )


class ParseFullText(ParseRecord):

    def parse_responses_to_records(self, responses):
        return (
            parse_html(response.data)
            for response in responses
        )


class ParseArkRecord(ParseRecord):

    def parse_responses_to_records(self, responses):
        for response in responses:
            years = get_years_published(response.data)
            code = response.query.get_code()
            yield ArkRecord(
                code=code,
                years=years
            )
