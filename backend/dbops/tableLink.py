import io
from dto.occurrenceRecord import OccurrenceRecord
from dto.paperRecord import PaperRecord


class TableLink:
    def __init__(self, conn, requestID=None):
        self.conn = conn
        self.records = []
        self.requestID = requestID

    def setRecords(self, records):
        self.records = records

    def insert(self):
        if len(self.records) > 0:
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
            'results',
            sep='|'
        )

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

    def getPaperCodesThatMatch(self, codes):
        cursor = self.conn.cursor()
        cursor.execute(
            f'SELECT code FROM papers WHERE code IN {codes}'
        )
        return cursor.fetchall()
