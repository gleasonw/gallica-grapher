
class OccurrenceRecord:

    def __init__(self, paperCode, url, date):
        self.url = url
        self.date = date
        self.paperCode = paperCode
        self.keyword = None
        self.ticketID = None
        self.requestID = None
        dateText = f'{date.year}-{date.month}-{date.day}'
        self.uniquenessCheck = f'{self.paperCode}{dateText}'

    def addFinalRowElements(self, ticketID, requestID, term):
        self.ticketID = ticketID
        self.requestID = requestID
        self.keyword = term

    def getRow(self):
        return [
            self.url,
            self.date.getDate()[0],
            self.date.getDate()[1],
            self.date.getDate()[2],
            self.keyword,
            self.paperCode,
            self.ticketID,
            self.requestID
        ]

