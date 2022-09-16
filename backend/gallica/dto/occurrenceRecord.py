
class OccurrenceRecord:

    def __init__(self, paperCode, url, date):
        self.url = url
        self.date = date
        self.paperCode = paperCode
        self.term = None
        self.ticketID = None
        self.requestID = None
        self.uniqueKey = None

    def __repr__(self):
        return f'OccurrenceRecord({self.paperCode}, {self.url}, {self.date})'

    def addFinalRowElements(self, ticketID, requestID, term):
        self.ticketID = ticketID
        self.requestID = requestID
        self.term = term
        dateText = f'{self.date.getDate()[0]}-{self.date.getDate()[1]}-{self.date.getDate()[2]}'
        self.uniqueKey = (
            self.paperCode,
            dateText,
            self.term
        )

    def getRow(self):
        return (
            self.url,
            self.date.getDate()[0],
            self.date.getDate()[1],
            self.date.getDate()[2],
            self.term,
            self.paperCode,
            self.ticketID,
            self.requestID
        )
