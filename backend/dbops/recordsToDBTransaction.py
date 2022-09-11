import io


class RecordsToDBTransaction:

    def __init__(
            self,
            requestID,
            ticketID,
            conn,
            getPaperRecordsForMissingCodes
    ):
        self.ticketID = ticketID
        self.requestID = requestID
        self.conn = conn
        self.getPaperRecordsForCodes = getPaperRecordsForMissingCodes

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

    def insertResults(self, records):
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
        missingPaperCodes = self.getMissingPapers()
        if missingPaperCodes:
            missingPaperRecords = self.getPaperRecordsForCodes(
                missingPaperCodes
            )
            self.insertPapers(missingPaperRecords)

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
            formattedCodes = [code[0] for code in curs.fetchall()]
            return formattedCodes

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
