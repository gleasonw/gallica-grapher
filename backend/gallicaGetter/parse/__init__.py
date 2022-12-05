from gallicaGetter.parse.arkRecord import ParseArkRecord
from gallicaGetter.parse.contentRecord import ParseContentRecord
from gallicaGetter.parse.fullText import ParseFullText
from gallicaGetter.parse.occurrenceRecords import ParseOccurrenceRecords
from gallicaGetter.parse.paperRecords import ParsePaperRecords
from gallicaGetter.parse.periodRecords import ParseGroupedRecordCounts


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


