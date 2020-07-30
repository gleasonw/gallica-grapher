import csv
import re
from gallicaLimitedHunter import GallicaLimitedHunter
from gallicaUnlimitedHunter import GallicaUnlimitedHunter
from gallicaHunter import GallicaHunter

from gallicaPackager import GallicaPackager


class HuntOverseer:
    def __init__(self, searchTerm, recordNumber, newspaper, yearRange, setLimitQueries, setStrict):
        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.query = None
        self.numberQueriesToGallica = None
		self.isMassiveSearch = None
        self.searchTerm = searchTerm
        self.recordNumber = recordNumber
        self.newspaper = newspaper
        self.newspaperDictionary = {}
        self.collectedQueries = []
        self.limitQueries = setLimitQueries
        self.strictYearRange = setStrict
		
        self.establishYearRange(yearRange)
        self.parseNewspaperDictionary()
        self.buildQuery()
        self.initiateQuery()
		
		self.currentRetrievedHits = 0
		self.startRecordForGallicaQuery = 0
		
	def checkIfHitDateinQueryRange(self, dateToCheck):
        yearList = dateToCheck.split("-")
        lower = int(yearList[0])
        higher = int(yearList[1])
        if lower < self.lowYear or higher > self.highYear:
            return False
        else:
            return True

    # What if list of papers?
    def parseNewspaperDictionary(self):
		if self.newspaper == "massive":
			self.isMassiveSearch = True
        elif self.strictYearRange:
            if self.newspaper == "all":
                self.establishStrictNewspaperDictionary()
            else:
                self.establishStrictTrimmedNewspaperDictionary()
        else:
            if self.newspaper == "all":
                self.establishLooseNewspaperDictionary()
            else:
                self.establishLooseTrimmedNewspaperDictionary()

    def establishStrictNewspaperDictionary(self):
        with open("CleanDates Journals 1777-1950.csv", "r", encoding="utf8") as inFile:
            reader = csv.reader(inFile)
            next(reader)
            for newspaperHit in reader:
                publicationRange = newspaperHit[1]
                if not self.checkIfHitDateinQueryRange(publicationRange):
                    continue
                else:
                    gallicaCode = newspaperHit[4]
                    newspaperName = newspaperHit[0]
                    self.newspaperDictionary.update({newspaperName: gallicaCode})

    def establishLooseNewspaperDictionary(self):
        with open("CleanDates Journals 1777-1950.csv", "r", encoding="utf8") as inFile:
            reader = csv.reader(inFile)
            next(reader)
            for newspaperHit in reader:
                publicationRange = newspaperHit[1]
                gallicaCode = newspaperHit[4]
                newspaperName = newspaperHit[0]
                self.newspaperDictionary.update({newspaperName: gallicaCode})

    def establishStrictTrimmedNewspaperDictionary(self):
       # Gonna have to fix this eventually. Need better capability to find the right newspapers in the CSV. Database
        # time?
		with open("CleanDates Journals 1777-1950.csv", "r", encoding="utf8") as inFile:
            reader = csv.reader(inFile)
            next(reader)
            for newspaperHit in reader:
                publicationRange = newspaperHit[1]
                newspaperName = newspaperHit[0]
                if (not self.checkIfHitDateinQueryRange(publicationRange)) or (self.newspaper != newspaperName):
                    continue
                else:
                    gallicaCode = newspaperHit[4]
                    self.newspaperDictionary.update({newspaperName: gallicaCode})

    def establishLooseTrimmedNewspaperDictionary(self):
        # Gonna have to fix this eventually. Need better capability to find the right newspapers in the CSV. Database
        # time?
        with open("CleanDates Journals 1777-1950.csv", "r", encoding="utf8") as inFile:
            reader = csv.reader(inFile)
            next(reader)
            for newspaperHit in reader:
                newspaperName = newspaperHit[0]
                if newspaperName != self.newspaper:
                    continue
                else:
                    gallicaCode = newspaperHit[4]
                    self.newspaperDictionary.update({newspaperName: gallicaCode})

    def establishYearRange(self, yearRange):
        yearRange = re.split(r'[;,\-\s*]', yearRange)
        if len(yearRange) == 2:
            self.lowYear = int(yearRange[0])
            self.highYear = int(yearRange[1])
            self.isYearRange = True
        else:
            self.isYearRange = False

    def buildQuery(self):
        if self.isYearRange:
            if (self.newspaper == "massive"):
                self.query = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and (gallica adj "{' \
                             'searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending '
            else:
                self.query = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{' \
                             'newsKey}}") and (gallica adj "{searchWord}")) sortby dc.date/sort.ascending '
            self.query = self.query.format(firstYear=str(self.lowYear), secondYear=str(self.highYear))
        else:
            if (self.newspaper == "massive"):
                self.query = '(gallica adj "{searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending'
            else:
                self.query = 'arkPress all "{{newsKey}}" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending'
        self.query = self.query.format(searchWord=self.searchTerm)

    def initiateQuery(self):
		if self.isMassiveSearch:
			if self.limitQueries:	
				self.runLimitedMassiveSearch()
			else:
				self.runUnlimitedMassiveSearch()
		elif self.limitQueries:
			self.runLimitedSearchOnDictionary()
		else:
			self.runUnlimitedSearchOnDictonary()
		self.packageQuery()

    def runUnlimitedSearchOnDictionary(self):
		for newspaper in self.newspaperDictionary:
            self.startRecordForGallicaQuery = 0
            self.currentRetrievedHits = 0
            newspaperCode = self.newspaperDictionary[newspaper]
            self.query = self.query.format(newsKey=newspaperCode)
            hunterForTotalNumberOfQueryResults = GallicaHunter(self.query, self.startRecordForGallicaQuery)
            numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits()
			while numberResultsForNewspaper > self.currentRetrievedHits:
				self.sendQuery()
				self.reportNewspaperProgress(newspaper, numberResultsForNewspaper)
				
    def runLimitedSearchOnDictionary(self):
		reachedLimit = False
		for newspaper in self.newspaperDictionary:
            self.startRecordForGallicaQuery = 0
            self.currentRetrievedHits = 0
            newspaperCode = self.newspaperDictionary[newspaper]
            self.query = self.query.format(newsKey=newspaperCode)
            hunterForTotalNumberOfQueryResults = GallicaHunter(self.query, self.startRecordForGallicaQuery)
            numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits()
            while numberResultsForNewspaper > self.currentRetrievedHits:
				self.reportProgress()
				self.sendQuery()
				if len(self.collectedQueries) >= self.recordNumber:
					reachedLimit = True
					break
			if reachedLimit:
				break
				
	def runLimitedMassiveSearch(self):
		reachedLimit = False
		hunterForTotalNumberOfQueryResults = GallicaHunter(self.query, self.startRecordForGallicaQuery)
        numberResultsForQuery = hunterForTotalNumberOfQueryResults.establishTotalHits()
		while numberResultsForQuery > self.currentRetrievedResults:
			self.sendQuery()
			if len(self.collectedQueries) >= self.recordNumber:
				reachedLimit = True
				break
		if reachedLimit:
			break
				
	def runUnlimitedMassiveSearch(self):
		hunterForTotalNumberOfQueryResults = GallicaHunter(self.query, self.startRecordForGallicaQuery)
        numberResultsForQuery = hunterForTotalNumberOfQueryResults.establishTotalHits()
		while numberResultsForQuery > self.currentRetrievedResults:
			self.sendQuery()		
				
				
	def sendQuery(self):
		hunter = GallicaHunter(self.query, self.startRecordForGallicaQuery)
		hunter.hunt()
		results = hunter.getResultList()
		self.currentRetrievedHits = self.currentRetrievedHits + len(results)
		self.collectedQueries = self.collectedQueries + results
		self.startRecordForGallicaQuery = self.startRecordForGallicaQuery + 51


    def packageQuery(self):
        filePacker = GallicaPackager(self.searchTerm, self.newspaper, self.collectedQueries,
                                     [self.lowYear, self.highYear])
        filePacker.makeCSVFile()
        filePacker.makeGraph()

    def establishNumberQueries(self):
        if type(self.recordNumber) is int
            self.numberQueriesToGallica = self.recordNumber // 50
	
	def reportNewspaperProgress(self, newspaper, numberNewspaperResults):
		progress = str(((len(self.currentRetrievedHits) / numberNewspaperResults) * 100))
		print(newspaper, "\n" + progress + "% complete" + "\n\n")
	
	def reportProgress(self):
        progress = str(((len(self.collectedQueries) / self.recordNumber) * 100))
        print(progress + "% complete overall")




