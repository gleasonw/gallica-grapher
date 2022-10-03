
class OccurrenceRecord:

    def __init__(self, paperTitle, paperCode, url, date):
        self.url = url
        self.date = date
        self.paperTitle = paperTitle
        self.paperCode = paperCode
        self.term = None
        self.ticketID = None
        self.requestID = None
        self.uniqueKey = None

    def getDate(self):
        return self.date

    def getPaperCode(self):
        return self.paperCode

    def __repr__(self):
        return f'OccurrenceRecord({self.paperTitle}, {self.url}, {self.date})'

    def addFinalRowElements(self, ticketID, requestID, term):
        self.ticketID = ticketID
        self.requestID = requestID
        self.term = term
        dateText = f'{self.date.getDate()[0]}-{self.date.getDate()[1]}-{self.date.getDate()[2]}'
        self.uniqueKey = (
            self.paperTitle,
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
            self.ticketID,
            self.requestID,
            self.paperCode,
            self.paperTitle
        )
