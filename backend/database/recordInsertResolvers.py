import io
import gallicaGetter


def insert_records_into_papers(records, conn):
    csvStream = buildCSVstream(records)
    with conn.cursor() as curs:
        curs.copy_from(
            csvStream,
            'papers',
            sep='|'
        )

#TODO: this doesn't appear to be working
def insert_records_into_results(records, identifier, stateHooks, conn):
    stream, codes = build_csv_stream_ensure_no_issue_duplicates(records)
    codes_in_db = set(
        match[0] for match in get_db_codes_that_match_these_codes(codes, conn)
    )
    missing_codes = codes - codes_in_db
    if missing_codes:
        insert_missing_codes_into_db(
            codes,
            onAddingMissingPapers=lambda: stateHooks.setSearchState(
                state='ADDING_MISSING_PAPERS',
                ticketID=identifier
            ),
            conn=conn
        )
        stateHooks.setSearchState(
            state='ADDING_RESULTS',
            ticketID=identifier
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


def insert_records_into_groupcounts(records, identifier, stateHooks, conn):
    csvStream = buildCSVstream(records)
    stateHooks.setSearchState(
        state='ADDING_RESULTS',
        ticketID=identifier
    )
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


def insert_missing_codes_into_db(codes, onAddingMissingPapers, conn):
    paperAPI = gallicaGetter.connect('papers')
    onAddingMissingPapers()
    paperRecords = paperAPI.get(list(codes))
    insert_records_into_papers(paperRecords, conn)


def get_db_codes_that_match_these_codes(codes, conn):
    with conn.cursor() as curs:
        curs.execute(
            'SELECT code FROM papers WHERE code IN %s',
            (tuple(codes),)
        )
        return curs.fetchall()


def build_csv_stream_ensure_no_issue_duplicates(records):
    csvFileLikeObject = io.StringIO()
    codes = set()
    codeDates = {}
    for record in records:
        recordPaper = record.get_paper_code()
        if recordPaper in codes:
            if datesForCode := codeDates.get(recordPaper):
                recordDate = record.get_date()
                if datesForCode.get(recordDate):
                    continue
                else:
                    datesForCode[recordDate] = True
            else:
                codeDates[record.get_paper_code()] = {record.get_date(): True}
        else:
            codes.add(record.get_paper_code())
        writeToCSVstream(csvFileLikeObject, record)
    csvFileLikeObject.seek(0)
    return csvFileLikeObject, codes


def buildCSVstream(records):
    csvFileLikeObject = io.StringIO()
    for record in records:
        writeToCSVstream(csvFileLikeObject, record)
    csvFileLikeObject.seek(0)
    return csvFileLikeObject


def writeToCSVstream(stream, record):
    stream.write("|".join(map(
        cleanCSVrow,
        record.getRow()
    )) + '\n')


def cleanCSVrow(value):
    if value is None:
        return r'\N'
    return str(value).replace('|', '\\|')