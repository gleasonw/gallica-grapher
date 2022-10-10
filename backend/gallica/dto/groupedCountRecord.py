class GroupedCountRecord:

    def __init__(self, date, count):
        self.date = date
        self.count = count
        self.term = None
        self.ticketID = None
        self.requestID = None
        self.uniqueKey = None

    def __repr__(self):
        return f'GroupedCountRecord({self.date}, {self.count})'

    def addFinalRowElements(self, ticketID, requestID, term):
        self.ticketID = ticketID
        self.requestID = requestID
        self.term = term
