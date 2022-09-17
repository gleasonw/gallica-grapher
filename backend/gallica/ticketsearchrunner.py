from lxml.etree import LxmlError

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
        self.onUpdateProgress = None
        self.numResultsRetrieved = 0

    def setProgressTracker(self, progressTracker):
        self.onUpdateProgress = progressTracker

    def search(self):
        queriesWithResponseXML = self.SRUfetch.fetchAllAndTrackProgress(
            self.ticket.queries,
            self.progressTrackWithPaper
        )
        records = self.convertQueriesToRecords(queriesWithResponseXML)
        uniqueRecords = self.removeDuplicateRecords(records)
        recordsWithPapersInDB = self.insertMissingPapersToDB(uniqueRecords)
        self.schema.insertRecordsIntoResults(recordsWithPapersInDB)
        self.numResultsRetrieved = self.schema.getNumResultsForTicket(self.ticket.key)
        self.ticket.setNumResultsRetrieved(self.numResultsRetrieved)

    def convertQueriesToRecords(self, queries):
        for query in queries:
            records = self.parse.occurrences(query.responseXML)
            for record in records:
                record.addFinalRowElements(
                    ticketID=self.ticket.key,
                    requestID=self.requestID,
                    term=query.term
                )
                yield record

    def removeDuplicateRecords(self, records):
        seen = set()
        uniqueRecords = []
        for record in records:
            if record.uniqueKey not in seen:
                seen.add(record.uniqueKey)
                uniqueRecords.append(record)
        return uniqueRecords

    def insertMissingPapersToDB(self, records):
        codesFromRecords = set(record.paperCode for record in records)
        schemaMatches = self.schema.getPaperCodesThatMatch(codesFromRecords)
        setOfCodesInDB = set(match[0] for match in schemaMatches)
        missingCodes = codesFromRecords - setOfCodesInDB
        if missingCodes:
            self.addTheseCodesToDB(list(missingCodes))
        return records

    def progressTrackWithPaper(self, query, numWorkers):
        try:
            paper = self.parse.onePaperTitleFromOccurrenceBatch(
                query.responseXML
            )
        except LxmlError:
            paper = 'Gallica hiccup'
        self.onUpdateProgress(
            query=query,
            numWorkers=numWorkers,
            randomPaper=paper
        )
