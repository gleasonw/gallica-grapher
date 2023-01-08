import gallicaGetter.parse.issueYearRecord as issues
import gallicaGetter.parse.contentRecord as content
import gallicaGetter.parse.fullText as fullText
import gallicaGetter.parse.paperRecords as paperRecords
import gallicaGetter.parse.periodRecords as periodRecords
import gallicaGetter.parse.volumeRecords as volumeRecords


def build_parser(desired_record):
    record_parsers = {
        "issues": issues.parse_responses_to_records,
        "groupedCount": periodRecords.parse_responses_to_records,
        "occurrence": volumeRecords.parse_responses_to_records,
        "paper": paperRecords.parse_responses_to_records,
        "content": contentRecord.parse_responses_to_records,
        "fullText": fullText.parse_responses_to_records,
    }
    if desired_record not in record_parsers:
        raise ValueError(
            f"Unrecognized record type: {desired_record}. Options include: {record_parsers.keys()}"
        )
    return record_parsers[desired_record]
