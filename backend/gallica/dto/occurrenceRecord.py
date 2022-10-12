class OccurrenceRecord:

    def __init__(
            self,
            paperTitle,
            paperCode,
            url,
            date,
            term,
            ticketID,
            requestID
    ):
        self.url = url
        self.date = date
        self.paperTitle = paperTitle
        self.paperCode = paperCode
        self.term = term
        self.ticketID = ticketID
        self.requestID = requestID

    def getDate(self):
        return self.date

    def getPaperCode(self):
        return self.paperCode

    def __repr__(self):
        return f'OccurrenceRecord({self.paperTitle}, {self.url}, {self.date})'

    def getRow(self):
        return (
            self.url,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.term,
            self.ticketID,
            self.requestID,
            self.paperCode,
            self.paperTitle
        )
