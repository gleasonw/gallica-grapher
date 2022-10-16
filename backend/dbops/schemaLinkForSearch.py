import io
from paperSearchFactory import PaperSearchFactory


class SchemaLinkForSearch:
    def __init__(
            self,
            tools,
            requestID=None
    ):
        self.conn = tools.dbConn
        self.requestID = requestID
        self.paperAPI = PaperSearchFactory(
           parse=tools.parse,
           SRUapi=tools.SRUapi
        ).buildSearch()

    def insertRecordsIntoPapers(self, records):
        csvStream = self.buildCSVstream(records)
        with self.conn.cursor() as curs:
            curs.copy_from(
                csvStream,
                'papers',
                sep='|'
            )

    def insertRecordsIntoResults(self, records, requestStateHandlers):
        stream, codes = self.buildCSVstreamAndGetCodesAndEnsureNoDuplicates(records)
        self.insertMissingPapersToDB(codes, requestStateHandlers['onAddingMissingPapers'])
        requestStateHandlers['onAddingResultsToDB']()
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

    def insertRecordsIntoGroupCounts(self, records, requestStateHandlers):
        csvStream = self.buildCSVstream(records)
        requestStateHandlers['onAddingResultsToDB']()
        with self.conn.cursor() as curs:
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

    def insertMissingPapersToDB(self, codes, onAddingMissingPapers):
        schemaMatches = self.getPaperCodesThatMatch(codes)
        setOfCodesInDB = set(match[0] for match in schemaMatches)
        missingCodes = codes - setOfCodesInDB
        if missingCodes:
            onAddingMissingPapers()
            paperRecords = self.paperAPI.getRecordsForTheseCodes(
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

