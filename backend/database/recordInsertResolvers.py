import io
import gallicaGetter
from database.connContext import getConn


def insertRecordsIntoPapers(records):
    csvStream = buildCSVstream(records)
    conn = getConn()
    with conn.cursor() as curs:
        curs.copy_from(
            csvStream,
            'papers',
            sep='|'
        )


def insertRecordsIntoResults(records, identifier, stateHooks):
    stream, codes = build_csv_stream_ensure_no_issue_duplicates(records)
    insertMissingPapersToDB(
        codes,
        onAddingMissingPapers=lambda: stateHooks.setSearchState(
            state='ADDING_MISSING_PAPERS',
            ticketID=identifier
        )
    )
    stateHooks.setSearchState(
        state='ADDING_RESULTS',
        ticketID=identifier
    )
    conn = getConn()
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


def insertRecordsIntoGroupCounts(records, identifier, stateHooks):
    csvStream = buildCSVstream(records)
    stateHooks.setSearchState(
        state='ADDING_RESULTS',
        ticketID=identifier
    )
    conn = getConn()
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


def insertMissingPapersToDB(codes, onAddingMissingPapers):
    codes_in_db = set(match[0] for match in getPaperCodesThatMatch(codes))
    missingCodes = codes - codes_in_db
    paperAPI = gallicaGetter.connect('papers')
    if missingCodes:
        onAddingMissingPapers()
        paperRecords = paperAPI.get(list(missingCodes))
        insertRecordsIntoPapers(paperRecords)


def getPaperCodesThatMatch(codes):
    conn = getConn()
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
        recordPaper = record.getPaperCode()
        if recordPaper in codes:
            if datesForCode := codeDates.get(recordPaper):
                recordDate = record.getDate()
                if datesForCode.get(recordDate):
                    continue
                else:
                    datesForCode[recordDate] = True
            else:
                codeDates[record.getPaperCode()] = {record.getDate(): True}
        else:
            codes.add(record.getPaperCode())
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