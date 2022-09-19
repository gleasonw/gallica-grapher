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
        responseData = self.SRUfetch.fetchAllAndTrackProgress(
            self.ticket.queries,
            self.progressTrackWithPaper
        )
        self.pipeRecordsToDB(responseData)
        self.schema.removeDuplicateRecordsInTicket(self.ticket.key)
        self.numResultsRetrieved = self.schema.getNumResultsForTicket(self.ticket.key)
        self.ticket.setNumResultsRetrieved(self.numResultsRetrieved)

    def pipeRecordsToDB(self, returnValues):
        for data, term in returnValues:
            records = list(self.parse.occurrences(
                xml=data,
                startYear=self.ticket.startYear
            ))
            if records is None:
                print("Empty records???")
                continue
            for record in records:
                record.addFinalRowElements(
                    ticketID=self.ticket.key,
                    requestID=self.requestID,
                    term=term
                )
            recordsWithPapersInDB = self.insertMissingPapersToDB(records)
            self.schema.insertRecordsIntoResults(recordsWithPapersInDB)

    #TODO: investigate why codes are null sometimes
    def insertMissingPapersToDB(self, records):
        codesFromRecords = set(record.paperCode for record in records)
        if not codesFromRecords:
            print("Need to fix this bug")
            return records
        schemaMatches = self.schema.getPaperCodesThatMatch(codesFromRecords)
        setOfCodesInDB = set(match[0] for match in schemaMatches)
        missingCodes = codesFromRecords - setOfCodesInDB
        if missingCodes:
            self.addTheseCodesToDB(list(missingCodes))
        return records

    def progressTrackWithPaper(self, data, elapsed, numWorkers):
        try:
            paper = self.parse.onePaperTitleFromOccurrenceBatch(data)
        except LxmlError:
            paper = 'Gallica hiccup'
        self.onUpdateProgress(
            elapsedTime=elapsed,
            numWorkers=numWorkers,
            randomPaper=paper
        )
