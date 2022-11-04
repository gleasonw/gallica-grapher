class GroupedCountRecord:

    def __init__(self, date, count, ticketID, term, requestID):
        self.date = date
        self.count = count
        self.term = term
        self.ticketID = ticketID
        self.requestID = requestID

    def getRow(self):
        row = [
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.term
        ]
        self.ticketID and row.append(self.ticketID)
        self.requestID and row.append(self.requestID)
        row.append(self.count)
        return tuple(row)

    def __repr__(self):
        return f'GroupedCountRecord({self.date}, {self.term}, {self.count})'


