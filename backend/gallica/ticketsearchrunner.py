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
        self.numQueriesFailed = 0

    def setProgressTracker(self, progressTracker):
        self.onUpdateProgress = progressTracker

    def search(self):
        responseData = self.SRUfetch.fetchAllAndTrackProgress(
            self.ticket.queries,
            self.progressTrackWithPaper
        )
        records, retries = self.parseRecords(responseData)
        if retries:
            resolvedRecords = self.retryFailedQueriesOnce(retries)
            records.extend(resolvedRecords)
        self.pipeRecordsToDB(records)
        self.schema.removeDuplicateRecordsInTicket(self.ticket.key)
        self.numResultsRetrieved = self.schema.getNumResultsForTicket(self.ticket.key)
        self.ticket.setNumResultsRetrieved(self.numResultsRetrieved)

    def parseRecords(self, responseValues):
        queriesToRetry = []
        parsedRecords = []
        for data, query in responseValues:
            records = self.parse.occurrences(
                xml=data,
                startYear=self.ticket.startYear
            )
            if records is None:
                print(f'No records found for query: {query}')
                queriesToRetry.append(query)
            for record in records:
                record.addFinalRowElements(
                    ticketID=self.ticket.key,
                    requestID=self.requestID,
                    term=query.term
                )
                parsedRecords.append(record)
        return parsedRecords, queriesToRetry

    def retryFailedQueriesOnce(self, queriesToRetry):
        print('Retrying search for queries:')
        print(queriesToRetry)
        retryData = self.SRUfetch.fetchAll(queriesToRetry)
        resolved, failedQueries = self.parseRecords(retryData)
        if failedQueries:
            print('Failed to resolve queries:')
            print(failedQueries)
            self.numQueriesFailed = len(failedQueries)
        return resolved

    def pipeRecordsToDB(self, records):
        recordsWithPapersInDB = self.insertMissingPapersToDB(records)
        self.schema.insertRecordsIntoResults(recordsWithPapersInDB)

    def insertMissingPapersToDB(self, records):
        codesFromRecords = set(record.paperCode for record in records)
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
