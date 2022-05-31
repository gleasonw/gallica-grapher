import datetime
import psycopg2

from GettingAndGraphing.paperGetterFromGallica import PaperGetterFromGallica
from requests_toolbelt import sessions

from GettingAndGraphing.paperDictionary import DictionaryMaker
from GettingAndGraphing.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter


class TermQuery:

    @staticmethod
    def makeSession():
        gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter(timeout=25)
        gallicaHttpSession.mount("https://", adapter)
        gallicaHttpSession.mount("http://", adapter)
        return gallicaHttpSession

    def __init__(self,
                 searchTerm,
                 yearRange,
                 progressTrackerThread,
                 dbConnection,
                 newspaperList=None,
                 strictYearRange=False):

        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.baseQuery = None
        self.progressTrackerThread = progressTrackerThread
        self.requestID = progressTrackerThread.getRequestID()
        self.eliminateEdgePapers = strictYearRange
        self.totalResults = 0
        self.progress = 0
        self.newspaperList = newspaperList
        self.newspaperDictionary = {}
        self.collectedQueries = []
        self.searchTerm = searchTerm
        self.topTenPapers = None
        self.numResultsForEachPaper = {}
        self.establishYearRange(yearRange)
        self.buildQuery()
        self.recordCodeStrings = []
        self.currentEntryDataJustInCase = None
        self.dbConnection = dbConnection
        self.paperNameCounts = []
        self.gallicaHttpSession = TermQuery.makeSession()

    def getTopTenPapers(self):
        return self.topTenPapers

    def discoverTopTenPapers(self):
        try:
            cursor = self.dbConnection.cursor()
            cursor.execute("""
				SELECT count(requestResults.identifier) AS papercount, papers.papername
					FROM (SELECT identifier, paperid FROM results WHERE requestid = %s AND searchterm = %s) AS requestResults 
					INNER JOIN papers ON requestResults.paperid = papers.papercode 
					GROUP BY papers.papername 
					ORDER BY papercount DESC
					LIMIT 10;
			""", (self.requestID, self.searchTerm))
            self.topTenPapers = cursor.fetchall()
            pass
        except psycopg2.DatabaseError as error:
            print(error)

    def postResultsToDB(self):
        print("Num collected: ", len(self.collectedQueries))
        try:
            for hitList in self.collectedQueries:
                self.currentEntryDataJustInCase = hitList
                self.insertOneResultToTable(hitList)
        except psycopg2.IntegrityError as e:
            try:
                print(e)
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
						INSERT INTO results (identifier, date, searchterm, paperID, requestid)
						VALUES (%s, %s, %s, %s, %s);
						""",
                       (entry.get('identifier'), entryDate, self.searchTerm,
                        entry.get('journalCode'), self.requestID))

    def parseNewspaperDictionary(self):
        dicParser = DictionaryMaker(self.newspaperList, self.dbConnection)
        self.newspaperDictionary = dicParser.getDictionary()

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
        lowYear= str(self.lowYear)
        highYear = str(self.highYear)
        if not self.newspaperList:
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
        if not self.newspaperList:
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
        self.baseQuery = self.baseQuery.format(searchWord=self.searchTerm)
        
    def completeSearch(self):
        self.updateProgress(100, 100)
        if len(self.collectedQueries) != 0:
            self.postResultsToDB()
            self.discoverTopTenPapers()

    def updateProgress(self, iteration, total):
        percentComplete = int((iteration / total) * 100)
        self.progressTrackerThread.setProgress(percentComplete)

