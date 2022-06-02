import datetime
import psycopg2

from requests_toolbelt import sessions

from timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from gallicaPaperQuery import GallicaPaperQuery


class KeywordQuery:

    @staticmethod
    def makeSession():
        gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter(timeout=25)
        gallicaHttpSession.mount("https://", adapter)
        return gallicaHttpSession

    def __init__(self,
                 searchTerm,
                 yearRange,
                 requestID,
                 progressTracker,
                 dbConnection):

        self.keyword = searchTerm
        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.baseQuery = None
        self.requestID = requestID
        self.estimateNumResults = 0
        self.progress = 0
        self.results = []
        self.topPapers = None
        self.currentEntryDataJustInCase = None
        self.progressTracker = progressTracker
        self.dbConnection = dbConnection

        self.establishYearRange(yearRange)
        self.gallicaHttpSession = KeywordQuery.makeSession()
        self.buildQuery()

    def getKeyword(self):
        return self.keyword

    def getTopPapers(self):
        return self.topPapers

    def getEstimateNumResults(self):
        return self.estimateNumResults

    def discoverTopPapers(self):
        cursor = self.dbConnection.cursor()
        cursor.execute("""
        
        SELECT count(requestResults.identifier) AS papercount, papers.papername
            FROM (SELECT identifier, paperid 
                    FROM results WHERE requestid = %s AND searchterm = %s) 
                    AS requestResults 
            INNER JOIN papers ON requestResults.paperid = papers.papercode 
            GROUP BY papers.papername 
            ORDER BY papercount DESC
            LIMIT 10;
                
        """, (self.requestID, self.keyword))
        self.topPapers = cursor.fetchall()

    def postResultsToDB(self):
        try:
            for hitList in self.results:
                self.currentEntryDataJustInCase = hitList
                self.insertOneResultToTable(hitList)
        except psycopg2.IntegrityError:
            try:
                missingCode = self.currentEntryDataJustInCase.get('journalCode')
                paperFetcher = GallicaPaperQuery(self.dbConnection)
                paperFetcher.addPaperToDBbyCode(missingCode)
                self.insertOneResultToTable(self.currentEntryDataJustInCase)
            except psycopg2.DatabaseError:
                raise

    def insertOneResultToTable(self, entry):
        cursor = self.dbConnection.cursor()
        entryDateBits = entry.get('date').split('-')
        entryMonth = int(entryDateBits[1])
        entryYear = int(entryDateBits[0])
        entryDay = int(entryDateBits[2])
        entryDate = datetime.datetime(entryYear,
                                      entryMonth,
                                      entryDay)
        cursor.execute("""
        
        INSERT INTO results 
            (identifier, date, searchterm, paperID, requestid)
        VALUES (%s, %s, %s, %s, %s);
        
        """, (entry.get('identifier'), entryDate, self.keyword,
              entry.get('journalCode'), self.requestID))

    def establishYearRange(self, yearRange):
        if len(yearRange) == 2:
            self.lowYear = int(yearRange[0])
            self.highYear = int(yearRange[1])
            self.isYearRange = True
        else:
            self.isYearRange = False

    def buildQuery(self):
        if self.isYearRange:
            self.buildYearRangeQuery()
        else:
            self.buildDatelessQuery()

    def completeSearch(self):
        if len(self.results) != 0:
            self.postResultsToDB()
            self.discoverTopPapers()

    def updateProgress(self, addition):
        self.progressTracker(addition)
