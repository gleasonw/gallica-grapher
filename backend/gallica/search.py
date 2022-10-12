class Search:

    def __init__(
            self,
            queries,
            insertRecordsIntoDatabase,
            recordGetter,
            searchType,
            ticketID,
            numRecordsToFetch=None,
            requestStateHandlers=None
    ):
        self.queries = queries
        self.insertRecordsIntoDatabase = insertRecordsIntoDatabase
        self.recordGetter = recordGetter
        self.numRecordsToPutInDB = numRecordsToFetch
        self.ticketID = ticketID
        self.searchType = searchType
        self.requestStateHandlers = requestStateHandlers

    def run(self):
        records = self.recordGetter.getFromQueries(self.queries)
        return self.insertRecordsIntoDatabase(
            records=records,
            requestStateHandlers=self.requestStateHandlers
        )

    def getNumRecordsToBeInserted(self):
        return self.numRecordsToPutInDB

    def getTicketID(self):
        return self.ticketID

    def getSearchType(self):
        return self.searchType
