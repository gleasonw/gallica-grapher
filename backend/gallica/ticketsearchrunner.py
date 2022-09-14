class TicketSearchRunner:

    def __init__(
            self,
            parse,
            ticket,
            request,
            schemaLink,
            sruFetch,
            paperAdd
    ):
        self.parse = parse
        self.ticket = ticket
        self.requestID = request
        self.SRUfetch = sruFetch
        self.addTheseCodesToDB = paperAdd
        self.schema = schemaLink
        self.progressTracker = None

    def search(self):
        for chunk in self.ticket.queries:
            queriesWithResponseXML = self.SRUfetch(
                chunk,
                self.progressTrackWithPaper
            )
            records = (
                self.parse.occurrences(query.responseXML)
                for query in queriesWithResponseXML
            )
            uniqueRecords = self.removeDuplicateRecords(records)
            self.insertMissingPapersToDB(uniqueRecords)
            finalizedRecords = self.finalizeRecords(uniqueRecords)
            self.schema.insertRecordsIntoResults(finalizedRecords)

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
