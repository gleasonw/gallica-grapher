class Search:

    def __init__(
            self,
            queries,
            insertRecordsIntoDatabase,
            recordGetter,
            searchType,
            ticketID,
            numRecordsToFetch=None,
            onAddingResultsToDB=None
    ):
        self.queries = queries
        self.insertRecordsIntoDatabase = insertRecordsIntoDatabase
        self.recordGetter = recordGetter
        self.onAddingResultsToDB = onAddingResultsToDB
        self.numRecordsToPutInDB = numRecordsToFetch
        self.ticketID = ticketID
        self.searchType = searchType

    def run(self):
        records = self.recordGetter.getFromQueries(self.queries)
        self.onAddingResultsToDB and self.onAddingResultsToDB()
        return self.insertRecordsIntoDatabase(records)

    def getNumRecordsToBeInserted(self):
        return self.numRecordsToPutInDB

    def getTicketID(self):
        return self.ticketID

    def getSearchType(self):
        return self.searchType
