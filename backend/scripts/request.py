import io
import threading
from scripts.ticket import Ticket
from scripts.utils.psqlconn import PSQLconn
from scripts.utils.gallicaSession import GallicaSession
from scripts.newspaper import Newspaper


class Request(threading.Thread):
    def __init__(self, tickets, requestID):
        self.session = GallicaSession().getSession()
        self.DBconnection = PSQLconn().getConn()
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.ticketDicts = tickets
        self.finished = False
        self.tooManyRecords = False
        self.ticketProgressStats = self.initProgressStats()
        self.records = []
        self.requestID = requestID
        self.estimateNumRecords = 0

        super().__init__()

    def run(self):

        def sumEstimateNumberRecordsForAllTickets(tickets):
            total = 0
            for tick in tickets:
                total += tick.getEstimateNumberRecords()
            return total

        requestTickets = self.generateRequestTickets()
        estimate = sumEstimateNumberRecordsForAllTickets(requestTickets)
        if self.estimateIsUnderRecordLimit(estimate):
            for ticket in requestTickets:
                ticket.run()
                self.records.extend(ticket.getRecords())
            self.moveRecordsToDB()
            self.finished = True
        else:
            self.estimateNumRecords = estimate
            self.tooManyRecords = True

    def generateRequestTickets(self):
        tickets = []
        for key, ticket in self.ticketDicts.items():
            requestToRun = Ticket(
                ticket,
                key,
                self,
                self.DBconnection,
                self.session)
            tickets.append(requestToRun)
        return tickets

    def estimateIsUnderRecordLimit(self, estimate):
        dbSpaceRemainingWithBuffer = 10000000 - self.getNumberRowsInAllTables() - 10000
        absoluteLimit = 3000000
        return estimate < min(dbSpaceRemainingWithBuffer, absoluteLimit)

    def getNumberRowsInAllTables(self):
        with self.DBconnection.cursor() as curs:
            curs.execute(
                """
                SELECT sum(reltuples)::bigint AS estimate
                FROM pg_class
                WHERE relname IN ('results', 'papers');
                """
            )
            return curs.fetchone()[0]

    def initProgressStats(self):
        progressDict = {}
        for key, ticket in self.ticketDicts.items():
            progressDict[key] = {
                'progress': 0,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 0,
                'randomPaper': None,
                'estimateSecondsToCompletion': 0
            }
        return progressDict

    def isFinished(self):
        return self.finished

    def setTicketProgressStats(self, ticketKey, progressStats):
        self.ticketProgressStats[ticketKey] = progressStats

    def setTicketProgressTo100AndMarkAsDone(self, ticketKey):
        self.setTicketProgressStats(ticketKey, {
            'progress': 100,
            'numResultsDiscovered': self.numResultsDiscovered,
            'numResultsRetrieved': self.numResultsRetrieved,
            'randomPaper': None,
            'estimateSecondsToCompletion': 0
        })

    def moveRecordsToDB(self):
        with self.DBconnection.cursor() as curs:
            self.moveRecordsToHoldingResultsDB(curs)
            self.addMissingPapers(curs)
            self.moveRecordsToFinalTable(curs)

    # TODO: move state up? Why is keyword query doing this?
    def moveRecordsToHoldingResultsDB(self, curs):
        csvStream = self.generateResultCSVstream()
        curs.copy_from(
            csvStream,
            'holdingresults',
            sep='|',
            columns=(
                'identifier',
                'year',
                'month',
                'day',
                'searchterm',
                'paperid',
                'ticketid',
                'requestid',
            )
        )

    def addMissingPapers(self, curs):
        paperGetter = Newspaper(self.session)
        missingPapers = self.getMissingPapers(curs)
        if missingPapers:
            paperGetter.sendTheseGallicaPapersToDB(missingPapers)

    def getMissingPapers(self, curs):
        curs.execute(
            """
            WITH papersInResults AS 
                (SELECT DISTINCT paperid 
                FROM holdingResults 
                WHERE requestid = %s)

            SELECT paperid FROM papersInResults
            WHERE paperid NOT IN 
                (SELECT code FROM papers);
            """
            , (self.requestID,))
        return curs.fetchall()

    #TODO: talk to gallica about the indexing weirdness. Shouldn't need the select distinct.
    def moveRecordsToFinalTable(self, curs):
        curs.execute(
            """
            WITH resultsForRequest AS (
                DELETE FROM holdingresults
                WHERE requestid = %s
                RETURNING identifier, year, month, day, searchterm, paperid, ticketid, requestid
            )

            INSERT INTO results (identifier, year, month, day, searchterm, paperid, ticketid, requestid)
                (SELECT DISTINCT 
                identifier, year, month, day , searchterm, paperid, ticketid, requestid FROM resultsForRequest);
            """
            , (self.requestID,))

    def generateResultCSVstream(self):

        def cleanCSVvalue(value):
            if value is None:
                return r'\N'
            return str(value).replace('|', '\\|')

        csvFileLikeObject = io.StringIO()
        for record in self.records:
            yearMonDay = record.getDate()
            csvFileLikeObject.write(
                "|".join(map(cleanCSVvalue, (
                    record.getUrl(),
                    yearMonDay[0],
                    yearMonDay[1],
                    yearMonDay[2],
                    record.getKeyword(),
                    record.getPaperCode(),
                    record.getTicketID(),
                    self.requestID
                ))) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject

    def getProgressStats(self):
        return self.ticketProgressStats

    def setNumDiscovered(self, total):
        self.numResultsDiscovered = total

    def getNumDiscovered(self):
        return self.numResultsDiscovered

    def setNumActuallyRetrieved(self, count):
        self.numResultsRetrieved = count

    def getNumActuallyRetrieved(self):
        return self.numResultsRetrieved
