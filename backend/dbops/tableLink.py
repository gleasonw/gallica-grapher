import io


class TableLink:
    def __init__(self, conn, requestID=None):
        self.conn = conn
        self.requestID = requestID
        self.CSVstreamBuilder = CSVStream().generateCSVstreamFromRecords

    #TODO: fix startdate enddate for multiple papers
    def insertRecordsIntoPapers(self, records):
        csvStream = self.CSVstreamBuilder(records)
        self.conn.cursor().copy_from(
            csvStream,
            'papers',
            sep='|'
        )

    def insertRecordsIntoResults(self, records):
        csvStream = self.CSVstreamBuilder(records)
        self.conn.cursor().copy_from(
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
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT code FROM papers WHERE code IN %s',
            (tuple(codes),)
        )
        return cursor.fetchall()

    def getNumResultsForTicket(self, ticketID):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) FROM results WHERE ticketid = %s',
            (ticketID,)
        )
        return cursor.fetchone()[0]


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