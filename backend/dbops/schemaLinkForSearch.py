from gallica.factories.paperSearchFactory import PaperSearchFactory
import io


class SchemaLinkForSearch:
    def __init__(
            self,
            tools,
            requestID=None
    ):
        self.conn = tools.conn
        self.requestID = requestID
        self.paperAPI = PaperSearchFactory(
           dbLink=tools.dbLink,
           parse=tools.parse,
           SRUapi=tools.SRUapi
        )

    def insertRecordsIntoPapers(self, records):
        csvStream = self.buildCSVstream(records)
        with self.conn.cursor() as curs:
            curs.copy_from(
                csvStream,
                'papers',
                sep='|'
            )

    def insertRecordsIntoResults(self, props):
        stream, codes = self.buildCSVstreamAndGetCodesAndEnsureNoDuplicates(props['records'])
        self.insertMissingPapersToDB(codes, props['onAddMissingPapers'])
        props['onAddResults']()
        with self.conn.cursor() as curs:
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

    def insertRecordsIntoGroupCounts(self, records):
        csvStream = self.buildCSVstream(records)
        with self.conn.cursor() as curs:
            curs.copy_from(
                csvStream,
                'groupcounts',
                sep='|'
            )

    def insertMissingPapersToDB(self, codes, onAddMissingPapers):
        schemaMatches = self.getPaperCodesThatMatch(codes)
        setOfCodesInDB = set(match[0] for match in schemaMatches)
        missingCodes = codes - setOfCodesInDB
        if missingCodes:
            onAddMissingPapers()
            paperRecords = self.paperAPI.fetchRecordsForTheseCodes(
                list(missingCodes)
            )
            self.insertRecordsIntoPapers(paperRecords)

    def getPaperCodesThatMatch(self, codes):
        with self.conn.cursor() as curs:
            curs.execute(
                'SELECT code FROM papers WHERE code IN %s',
                (tuple(codes),)
            )
            return curs.fetchall()

    def buildCSVstreamAndGetCodesAndEnsureNoDuplicates(self, records):
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
            self.writeToCSVstream(csvFileLikeObject, record)
        csvFileLikeObject.seek(0)
        return csvFileLikeObject, codes

    def buildCSVstream(self, records):
        csvFileLikeObject = io.StringIO()
        for record in records:
            self.writeToCSVstream(csvFileLikeObject, record)
        csvFileLikeObject.seek(0)
        return csvFileLikeObject

    def writeToCSVstream(self, stream, record):
        stream.write("|".join(map(
            self.cleanCSVrow,
            record.getRow()
        )) + '\n')


    #TODO: optimize query, or discover a better way to remove duplicates
    def removeDuplicateRecordsInTicket(self, ticketID):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                WITH ticketRecords AS (
                    SELECT ctid, year, month, day, papercode, searchterm, ticketid, requestid
                    FROM results
                    WHERE ticketid = %s
                    AND requestid = %s
                )
                DELETE FROM results a USING (
                    SELECT MIN(ctid) as ctid, year, month, day, papercode, searchterm, ticketid, requestid
                    FROM ticketRecords
                    GROUP BY year, month, day, papercode, searchterm, ticketid, requestid
                    HAVING COUNT(*) > 1
                ) b
                WHERE a.requestid = b.requestid
                AND a.ticketid = b.ticketid
                AND a.year = b.year
                AND (a.month = b.month OR (a.month IS NULL AND b.month IS NULL))
                AND (a.day = b.day OR (a.day IS NULL AND b.day IS NULL))
                AND a.papercode = b.papercode
                AND a.searchterm = b.searchterm
                AND a.ctid <> b.ctid;
                """,
                (ticketID, self.requestID,)
            )

    def cleanCSVrow(self, value):
        if value is None:
            return r'\N'
        return str(value).replace('|', '\\|')

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

