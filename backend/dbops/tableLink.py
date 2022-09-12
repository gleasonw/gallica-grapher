import io
from dto.occurrenceRecord import OccurrenceRecord
from dto.paperRecord import PaperRecord

class TableLink:
    def __init__(self, conn, getPaperRecordsForCodes=None, requestID=None):
        self.conn = conn
        self.records = []
        self.getPaperRecordsForCodes = getPaperRecordsForCodes
        self.requestID=requestID

    def setRecords(self, records):
        self.records = records

    def insert(self):
        if self.records[0]:
            csvStream = self.generateResultCSVstream()
            if isinstance(self.records[0], PaperRecord):
                self.insertIntoPapersFrom(csvStream)
            elif isinstance(self.records[0], OccurrenceRecord):
                self.insertIntoResultsFrom(csvStream)
            else:
                raise Exception(f'Unknown record type: {type(self.records[0])}')
        else:
            raise Exception('No records to insert')

    def insertIntoPapersFrom(self, csvStream):
        self.conn.cursor().copy_from(
            csvStream,
            'papers',
            sep='|'
        )

    def insertIntoResultsFrom(self, csvStream):
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
        missingPaperCodes = self.getMissingPapers()
        if missingPaperCodes:
            self.addMissingPapers(missingPaperCodes)
        self.moveRecordsToFinalTable()

    def addMissingPapers(self, missingPaperCodes):
        missingPaperRecords = self.getPaperRecordsForCodes(
            missingPaperCodes
        )
        self.insertIntoPapersFrom(missingPaperRecords)

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

    def generateResultCSVstream(self):

        def cleanCSVrow(value):
            if value is None:
                return r'\N'
            return str(value).replace('|', '\\|')

        csvFileLikeObject = io.StringIO()
        for record in self.records:
            csvFileLikeObject.write("|".join(map(
                cleanCSVrow,
                record.getRow()
            )) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject
