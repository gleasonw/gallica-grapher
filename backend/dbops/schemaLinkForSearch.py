import io


class SchemaLinkForSearch:
    def __init__(self, conn, requestID=None):
        self.conn = conn
        self.requestID = requestID
        self.CSVstreamBuilder = CSVStream().generateCSVstreamFromRecords

    def insertRecordsIntoPapers(self, records):
        csvStream = self.CSVstreamBuilder(records)
        with self.conn.cursor() as curs:
            curs.copy_from(
                csvStream,
                'papers',
                sep='|'
            )

    def insertRecordsIntoResults(self, records):
        csvStream = self.CSVstreamBuilder(records)
        with self.conn.cursor() as curs:
            curs.copy_from(
                csvStream,
                'results',
                sep='|',
                columns=(
                    'identifier',
                    'year',
                    'month',
                    'day',
                    'searchterm',
                    'paperid',
                    'ticketid',
                    'requestid'
                )
            )

    def getPaperCodesThatMatch(self, codes):
        with self.conn.cursor() as curs:
            curs.execute(
                'SELECT code FROM papers WHERE code IN %s',
                (tuple(codes),)
            )
            return curs.fetchall()

    def getNumResultsForTicket(self, ticketID):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                SELECT COUNT(*) 
                FROM results 
                WHERE ticketid = %s
                AND requestid = %s
                """,
                (ticketID,self.requestID,)
            )
            return curs.fetchone()[0]

    def removeDuplicateRecordsInTicket(self, ticketID):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                WITH ticketRecords AS (
                    SELECT ctid, year, month, day, paperid, searchterm, ticketid, requestid
                    FROM results
                    WHERE ticketid = %s
                    AND requestid = %s
                )
                DELETE FROM results a USING (
                    SELECT MIN(ctid) as ctid, year, month, day, paperid, searchterm, ticketid, requestid
                    FROM ticketRecords
                    GROUP BY year, month, day, paperid, searchterm, ticketid, requestid
                    HAVING COUNT(*) > 1
                ) b
                WHERE a.requestid = b.requestid
                AND a.ticketid = b.ticketid
                AND a.year = b.year
                AND (a.month = b.month OR (a.month IS NULL AND b.month IS NULL))
                AND (a.day = b.day OR (a.day IS NULL AND b.day IS NULL))
                AND a.paperid = b.paperid
                AND a.searchterm = b.searchterm
                AND a.ctid <> b.ctid;
                """,
                (ticketID, self.requestID,)
            )


class CSVStream:

    def __init__(self):
        pass

    def generateCSVstreamFromRecords(self, records):
        csvFileLikeObject = io.StringIO()
        for record in records:
            csvFileLikeObject.write("|".join(map(
                self.cleanCSVrow,
                record.getRow()
            )) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject

    def cleanCSVrow(self, value):
        if value is None:
            return r'\N'
        return str(value).replace('|', '\\|')
