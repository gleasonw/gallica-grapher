from lxml.etree import LxmlError


class TicketSearchRunner:

    def __init__(
            self,
            parse,
            ticket,
            requestID,
            schemaLink,
            sruFetch
    ):
        self.parse = parse
        self.ticket = ticket
        self.requestID = requestID
        self.SRUfetch = sruFetch
        self.schema = schemaLink
        self.onUpdateProgress = None
        self.numResultsRetrieved = 0
        self.numQueriesFailed = 0

    def setProgressTracker(self, progressTracker):
        self.onUpdateProgress = progressTracker

    def search(self, props):
        responseData = self.SRUfetch.fetchAllAndTrackProgress(
            self.ticket.queries,
            self.progressTrackWithPaper
        )
        records = self.generateRecords(responseData)
        self.schema.insertRecordsIntoResults(
            {
                'records': records,
                'ticketID': self.ticket.key,
                'onAddMissingPapers': props['onAddMissingPapers'],
                'onAddResults': props['onAddResults'],
                'onRemoveDuplicateRecords': props['onRemoveDuplicateRecords']
            }
        )
        self.numResultsRetrieved = self.schema.getNumResultsForTicket(self.ticket.key)
        self.ticket.setNumResultsRetrieved(self.numResultsRetrieved)

    def generateRecords(self, responseValues):
        for data, query in responseValues:
            records = self.parse.occurrences(data)
            for record in records:
                record.addFinalRowElements(
                    ticketID=self.ticket.key,
                    requestID=self.requestID,
                    term=query.term
                )
                yield record

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
