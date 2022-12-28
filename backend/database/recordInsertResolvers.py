import io
from typing import List

import gallicaGetter
from gallicaGetter.parse.paperRecords import PaperRecord
from gallicaGetter.parse.periodRecords import PeriodRecord
from gallicaGetter.parse.volumeRecords import VolumeRecord


def insert_records_into_papers(records, conn):
    csvStream = build_csv_stream(records)
    with conn.cursor() as curs:
        curs.copy_from(
            csvStream,
            'papers',
            sep='|'
        )


def insert_records_into_results(
        records,
        requestID,
        ticketID,
        onAddingMissingPapers,
        conn):
    stream, codes = build_csv_stream_ensure_no_issue_duplicates(
        records=records,
        requestID=requestID,
        ticketID=ticketID,
    )
    codes_in_db = set(match[0] for match in get_db_codes_that_match_these_codes(codes, conn))
    missing_codes = codes - codes_in_db
    if missing_codes:
        onAddingMissingPapers and onAddingMissingPapers()
        insert_missing_codes_into_db(
            missing_codes,
            conn=conn
        )
    with conn.cursor() as curs:
        curs.copy_from(
            stream,
            'results',
            sep='|',
            columns=(
                'identifier',
                'year',
                'month',
                'day',
                'searchterm',
                'ticketid',
                'requestid',
                'papercode',
                'papertitle'
            )
        )


def insert_records_into_groupcounts(records, requestID, ticketID, conn):
    csvStream = build_csv_stream(records=records, requestID=requestID, ticketID=ticketID)
    with conn.cursor() as curs:
        curs.copy_from(
            csvStream,
            'groupcounts',
            sep='|',
            columns=(
                'year',
                'month',
                'day',
                'searchterm',
                'ticketid',
                'requestid',
                'count'
            )
        )


def insert_missing_codes_into_db(codes, conn):
    paperAPI = gallicaGetter.connect('papers')
    paperRecords = paperAPI.get(list(codes))
    insert_records_into_papers(paperRecords, conn)


def get_db_codes_that_match_these_codes(codes, conn):
    with conn.cursor() as curs:
        curs.execute(
            'SELECT code FROM papers WHERE code IN %s',
            (tuple(codes),)
        )
        return curs.fetchall()


def build_csv_stream_ensure_no_issue_duplicates(records: List[VolumeRecord], requestID: str, ticketID: str):
    csv_file_like_object = io.StringIO()
    codes = set()
    code_dates = {}
    for record in records:
        record_paper = record.paper_code
        if record_paper in codes:
            if datesForCode := code_dates.get(record_paper):
                record_date = record.date.getDate()
                if datesForCode.get(record_date):
                    continue
                else:
                    datesForCode[record_date] = True
            else:
                code_dates[record.paper_code] = {record.paper_code: True}
        else:
            codes.add(record.paper_code)
        write_to_csv_stream(
            stream=csv_file_like_object,
            record=record,
            requestID=requestID,
            ticketID=ticketID
        )
    csv_file_like_object.seek(0)
    print(f'unique codes: {codes}')
    return csv_file_like_object, codes


def build_csv_stream(records, requestID=None, ticketID=None):
    csv_file_like_object = io.StringIO()
    for record in records:
        write_to_csv_stream(
            stream=csv_file_like_object,
            record=record,
            requestID=requestID,
            ticketID=ticketID
        )
    csv_file_like_object.seek(0)
    return csv_file_like_object


def write_to_csv_stream(stream, record, requestID, ticketID):
    if isinstance(record, VolumeRecord):
        row = (
            record.url,
            record.date.getYear(),
            record.date.getMonth(),
            record.date.getDay(),
            record.term,
            ticketID,
            requestID,
            record.paper_code,
            record.paper_title
        )
    elif isinstance(record, PeriodRecord):
        row = (
            record.date.getYear(),
            record.date.getMonth(),
            record.date.getDay(),
            record.term,
            ticketID,
            requestID,
            record.count
        )
    elif isinstance(record, PaperRecord):
        row = (
            record.title,
            record.publishing_years[0],
            record.publishing_years[-1],
            record.continuous,
            record.code
        )
    else:
        raise Exception(f'Unknown record type{type(record)}')
    stream.write("|".join(map(
        clean_csv_row,
        row
    )) + '\n')


def clean_csv_row(value):
    if value is None:
        return r'\N'
    return str(value).replace('|', '\\|')
