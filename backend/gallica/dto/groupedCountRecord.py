class GroupedCountRecord:

    def __init__(self, date, count, ticketID, term, requestID):
        self.date = date
        self.count = count
        self.term = term
        self.ticketID = ticketID
        self.requestID = requestID

    def getRow(self):
        return (
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.term,
            self.ticketID,
            self.requestID,
            self.count
        )

    def __repr__(self):
        return f'GroupedCountRecord({self.date}, {self.count})'
