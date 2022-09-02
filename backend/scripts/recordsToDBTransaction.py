from scripts.paperRecordFetch import PaperRecordFetch
import io


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
            raise ValueError('Invalid target table')

    def insertPapers(self, records):
        csvStream = generateResultCSVstream(
            records,
            getPaperRecordRowIterable
        )
        self.copyCSVstreamToTable(csvStream, 'papers')

    def insertNgramOccurrenceRecords(self, records):
        csvStream = generateResultCSVstream(
            records,
            getKeywordRecordRowIterable
        )
        self.copyCSVstreamToTable(csvStream, 'holdingResults')
        self.addMissingPapers()
        self.moveRecordsToFinalTable()

    def copyCSVstreamToTable(self, csvStream, targetTable):
        self.conn.copy_from(
            csvStream,
            targetTable,
            sep='|',
            null=r'\N'
        )

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


def getPaperRecordRowIterable(paperRecord):
    return (
        paperRecord.getUrl(),
        paperRecord.getDate()[0],
        paperRecord.getDate()[1],
        paperRecord.isContinuous(),
        paperRecord.getPaperCode()
    )


def getKeywordRecordRowIterable(keywordRecord, requestid):
    return (
        keywordRecord.getUrl(),
        keywordRecord.getDate()[0],
        keywordRecord.getDate()[1],
        keywordRecord.getDate()[2],
        keywordRecord.getKeyword(),
        keywordRecord.getPaperCode(),
        keywordRecord.getTicketID(),
        requestid
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
