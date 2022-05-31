import datetime
import psycopg2

from GettingAndGraphing.paperGetterFromGallica import PaperGetterFromGallica
from requests_toolbelt import sessions

from GettingAndGraphing.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter


class TermQuery:

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
                 dbConnection,
                 papers=None,
                 strictYearRange=False):

        self.keyword = searchTerm
        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.baseQuery = None
        self.requestID = requestID
        self.eliminateEdgePapers = strictYearRange
        self.totalResults = 0
        self.progress = 0
        self.papersAndCodes = papers
        self.results = []
        self.topTenPapers = None
        self.numResultsInEachPaper = {}
        self.indexAndCodeStrings = []
        self.currentEntryDataJustInCase = None
        self.progressTracker = progressTracker
        self.dbConnection = dbConnection
        self.paperNameCounts = []

        self.establishYearRange(yearRange)
        self.gallicaHttpSession = TermQuery.makeSession()
        self.buildQuery()

    def getKeyword(self):
        return self.keyword

    def getTopTenPapers(self):
        return self.topTenPapers

    def discoverTopTenPapers(self):
        try:
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
            self.topTenPapers = cursor.fetchall()
            pass
        except psycopg2.DatabaseError as error:
            print(error)

    def postResultsToDB(self):
        try:
            for hitList in self.results:
                self.currentEntryDataJustInCase = hitList
                self.insertOneResultToTable(hitList)
        except psycopg2.IntegrityError:
            try:
                missingCode = self.currentEntryDataJustInCase.get('journalCode')
                paperFetcher = PaperGetterFromGallica(self.dbConnection)
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
        entryDate = datetime.datetime(entryYear, entryMonth, entryDay)
        cursor.execute("""
						INSERT INTO results 
						    (identifier, date, searchterm, paperID, requestid)
						VALUES (%s, %s, %s, %s, %s);
						""",
                       (entry.get('identifier'), entryDate, self.keyword,
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

    def buildYearRangeQuery(self):
        lowYear = str(self.lowYear)
        highYear = str(self.highYear)
        if not self.papers:
            self.baseQuery = f"""
                (dc.date >= "{lowYear}" and dc.date <= "{highYear}") 
                and (gallica adj "{{searchWord}}") 
                and (dc.type all "fascicule") 
                sortby dc.date/sort.ascending
            """
        else:
            self.baseQuery = f"""
                (dc.date >= "{lowYear}" and dc.date <= "{highYear}") 
                and ((arkPress all "{{newsKey}}_date"
                and (gallica adj "{{searchWord}}")) 
                sortby dc.date/sort.ascending
            """

    def buildDatelessQuery(self):
        if not self.papers:
            self.baseQuery = """
                (gallica adj "{searchWord}") 
                and (dc.type all "fascicule") 
                sortby dc.date/sort.ascending
            """
        else:
            self.baseQuery = """
                arkPress all "{{newsKey}}_date"
                and (gallica adj "{searchWord}")
                sortby dc.date/sort.ascending
            """
        self.baseQuery = self.baseQuery.format(searchWord=self.keyword)
        
    def completeSearch(self):
        if len(self.results) != 0:
            self.postResultsToDB()
            self.discoverTopTenPapers()

    def updateProgress(self, addition):
        self.progressTracker(addition)

