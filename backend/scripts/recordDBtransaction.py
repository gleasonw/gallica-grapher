from utils.psqlconn import PSQLconn


class RecordDBTransaction:

    def __init__(
            self,
            targetTable,
            records,
            requestID):
        self.targetTable = targetTable
        self.records = records
        self.requestID = requestID

    def generateResultCSVstream(self):

        def cleanCSVvalue(value):
            if value is None:
                return r'\N'
            return str(value).replace('|', '\\|')

        csvFileLikeObject = io.StringIO()
        for record in self.records:
            yearMonDay = record.getDate()
            csvFileLikeObject.write(
                "|".join(map(cleanCSVvalue, (
                    record.getUrl(),
                    yearMonDay[0],
                    yearMonDay[1],
                    yearMonDay[2],
                    record.getKeyword(),
                    record.getPaperCode(),
                    record.getTicketID(),
                    self.requestID
                ))) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject