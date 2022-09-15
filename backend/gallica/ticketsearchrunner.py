class TicketSearchRunner:

    def __init__(
            self,
            parse,
            ticket,
            requestID,
            schemaLink,
            sruFetch,
            paperAdd
    ):
        self.parse = parse
        self.ticket = ticket
        self.requestID = requestID
        self.SRUfetch = sruFetch
        self.addTheseCodesToDB = paperAdd
        self.schema = schemaLink
        self.progressTracker = None

    def search(self):
        for chunk in self.ticket.queries:
            queriesWithResponseXML = self.SRUfetch.fetchAllAndTrackProgress(
                chunk,
                self.progressTrackWithPaper
            )
            records = self.convertQueriesToRecords(queriesWithResponseXML)
            uniqueRecords = self.removeDuplicateRecords(records)
            self.insertMissingPapersToDB(uniqueRecords)
            finalizedRecords = self.finalizeRecords(uniqueRecords)
            self.schema.insertRecordsIntoResults(finalizedRecords)

    def convertQueriesToRecords(self, queries):
        for query in queries:
            records = self.parse.occurrences(query.responseXML)
            for record in records:
                record.addFinalRowElements(
                    ticketID=self.ticket.key,
                    requestID=self.ticket.requestID,
                    term=query.term
                )
                yield record

    def removeDuplicateRecords(self, records):
        seen = set()
        for record in records:
            if record.uniquenessCheck not in seen:
                seen.add(record.uniquenessCheck)
                yield record

    def insertMissingPapersToDB(self, records):
        codesFromRecords = set(record.code for record in records)
        schemaMatches = set(self.schema.getPaperCodesThatMatch(codesFromRecords))
        missingCodes = codesFromRecords - schemaMatches
        if missingCodes:
            self.addTheseCodesToDB(missingCodes)

    def finalizeRecords(self, records):
        for record in records:
            record.addFinalRowElements(
                ticketID=self.ticket.key,
                requestID=self.ticket.requestID,
                term=self.ticket.keyword
            )
            yield record

    def setProgressTracker(self, progressTracker):
        self.progressTracker = progressTracker

    def progressTrackWithPaper(self, query, numWorkers):
        paper = self.parse.onePaperTitleFromOccurrenceBatch(
            query.responseXML
        )
        self.progressTracker(
            query,
            numWorkers,
            paper
        )
