from scripts.paperRecordFetch import PaperRecordFetch
import io
from scripts.utils.psqlconn import PSQLconn

class RecordsToDBTransaction:

    def __init__(self, requestID, conn):
        self.requestID = requestID
        self.conn = conn

    def insert(self, targetTable, records):
        if targetTable == 'papers':
            self.insertPapers(records)
        elif targetTable == 'results':
            self.insertNgramOccurrenceRecords(records)
        else:
            raise ValueError(f'Invalid target table: {targetTable}')

    def insertPapers(self, records):
        csvStream = generateResultCSVstream(
            records,
            getPaperRecordRowIterable
        )
        self.conn.cursor().copy_from(
            csvStream,
            'papers',
            sep='|'
        )

    def insertNgramOccurrenceRecords(self, records):
        csvStream = generateResultCSVstream(
            records,
            self.getKeywordRecordRowIterable
        )
        self.conn.cursor().copy_from(
            csvStream,
            'holdingresults',
            sep='|',
            columns=(
                'identifier',
                'year',
                'month',
                'day',
                'searchterm',
                'paperid',
                'ticketid',
                'requestid',
            )
        )
        self.addMissingPapers()
        self.moveRecordsToFinalTable()

    def addMissingPapers(self):
        paperGetter = PaperRecordFetch()
        missingPaperCodes = self.getMissingPapers()
        if missingPaperCodes:
            missingPaperRecords = paperGetter.fetchRecordDataForCodes(
                missingPaperCodes
            )
            self.insert('papers', missingPaperRecords)

    def getMissingPapers(self):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                WITH papersInResults AS 
                    (SELECT DISTINCT paperid 
                    FROM holdingResults 
                    WHERE requestid = %s)
                SELECT paperid FROM papersInResults
                WHERE paperid NOT IN 
                    (SELECT code FROM papers);
                """
                , (self.requestID,))
            return curs.fetchall()

    def moveRecordsToFinalTable(self):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                WITH resultsForRequest AS (
                    DELETE FROM holdingresults
                    WHERE requestid = %s
                    RETURNING identifier, year, month, day, searchterm, paperid, ticketid, requestid
                )
                INSERT INTO results (identifier, year, month, day, searchterm, paperid, ticketid, requestid)
                    (SELECT identifier, year, month, day , searchterm, paperid, ticketid, requestid 
                    FROM resultsForRequest);
                """
                , (self.requestID,))

    def getKeywordRecordRowIterable(self, keywordRecord):
        return (
            keywordRecord.getUrl(),
            keywordRecord.getDate()[0],
            keywordRecord.getDate()[1],
            keywordRecord.getDate()[2],
            keywordRecord.getKeyword(),
            keywordRecord.getPaperCode(),
            keywordRecord.getTicketID(),
            self.requestID
        )


def getPaperRecordRowIterable(paperRecord):
    return (
        paperRecord.getPaperTitle(),
        paperRecord.getDate()[0],
        paperRecord.getDate()[1],
        paperRecord.isContinuous(),
        paperRecord.getPaperCode()
    )


def generateResultCSVstream(records, getRowIterable):

    def cleanCSVrow(value):
        if value is None:
            return r'\N'
        return str(value).replace('|', '\\|')

    csvFileLikeObject = io.StringIO()
    for record in records:
        csvFileLikeObject.write("|".join(map(
            cleanCSVrow,
            getRowIterable(record)
        )) + '\n')
    csvFileLikeObject.seek(0)
    return csvFileLikeObject


if __name__ == '__main__':
    fetcher = PaperRecordFetch()
    paperRecords = fetcher.fetchAllPaperRecords()
    dbInsert = RecordsToDBTransaction('papers', PSQLconn().getConn())
    dbInsert.insertPapers(paperRecords)
