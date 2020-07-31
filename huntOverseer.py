import csv
import re
import sys
from gallicaHunter import GallicaHunter

from gallicaPackager import GallicaPackager


class HuntOverseer:
    def __init__(self, *args):
        self.lowYear = None
        self.highYear = None
        self.isYearRange = None
        self.baseQuery = None
        self.numberQueriesToGallica = None
        self.isNoDictSearch = None
        self.strictYearRange = None
        self.recordNumber = None
        self.totalResults = 0
        self.newspaper = args[1]
        self.newspaperDictionary = {}
        self.collectedQueries = []
        self.searchTerm = args[0]
        self.topPapers = []
        self.numResultsForEachPaper = {}

        #indicates another class would be helpful for overseeing newspaper-wide queries
        self.currentProcessedResults = 0
        self.startRecordForGallicaQuery = 1
        self.currentNumValidResults = 0
        self.currentNumPurgedResults = None

        self.establishRecordNumber(args)
        self.establishStrictness(args[3])
        self.establishYearRange(args[2])
        self.parseNewspaperDictionary()
        self.buildQuery()
        self.initiateQuery()

    def establishRecordNumber(self, argList):
        if len(argList) == 5:
            self.recordNumber = int(argList[4])


    # Good time to parse errors in formatting too
    def establishStrictness(self, strictSetting):
        if strictSetting in ["ya", "True", "true", "yes", "absolutely"]:
            self.strictYearRange = True
        else:
            self.strictYearRange = False

    def checkIfHitDateinQueryRange(self, dateToCheck):
        yearList = dateToCheck.split("-")
        lower = int(yearList[0])
        higher = int(yearList[1])
        if lower < self.lowYear and higher > self.highYear:
            return True
        else:
            return False

    # What if list of papers?
    def parseNewspaperDictionary(self):
        if self.newspaper == "noDict":
            self.isNoDictSearch = True
        else:
            self.isNoDictSearch = False
            if self.strictYearRange:
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
            if self.newspaper == "noDict":
                self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and (gallica adj "{' \
                             '{searchWord}}") and (dc.type all "fascicule") sortby dc.date/sort.ascending '
            else:
                self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{{{' \
                             'newsKey}}}}") and (gallica adj "{{searchWord}}")) sortby dc.date/sort.ascending '
            self.baseQuery = self.baseQuery.format(firstYear=str(self.lowYear), secondYear=str(self.highYear))
        else:
            if self.newspaper == "noDict":
                self.baseQuery = '(gallica adj "{searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending'
            else:
                self.baseQuery = 'arkPress all "{{newsKey}}" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending'
        self.baseQuery = self.baseQuery.format(searchWord=self.searchTerm)

    def initiateQuery(self):
        if self.isNoDictSearch:
            if self.recordNumber is not None:
                self.runLimitednoDictSearch()
            else:
                self.runUnlimitednoDictSearch()
        else:
            if self.recordNumber is not None:
                self.runLimitedSearchOnDictionary()
            else:
                self.runUnlimitedSearchOnDictionary()
                self.printTopTenPapers()
        self.packageQuery()

    def runUnlimitedSearchOnDictionary(self):
        self.findTotalResultsForUnlimitedNewspaperSearch()
        for newspaper in self.newspaperDictionary:
            self.currentNumPurgedResults = 0
            self.startRecordForGallicaQuery = 1
            self.currentProcessedResults = 0
            self.currentNumValidResults = 0
            numberResultsForNewspaper = self.numResultsForEachPaper[newspaper]
            newspaperCode = self.newspaperDictionary[newspaper]
            newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
            while numberResultsForNewspaper > self.currentProcessedResults:
                self.sendQuery(newspaperQuery)
                HuntOverseer.reportProgress(len(self.collectedQueries), self.totalResults, "retrieving results")
            if self.currentNumValidResults > 0:
                self.topPapers.append([newspaper, self.currentNumValidResults])

    def runLimitedSearchOnDictionary(self):
        reachedLimit = False
        for newspaper in self.newspaperDictionary:
            self.currentNumPurgedResults = 0
            self.startRecordForGallicaQuery = 1
            self.currentProcessedResults = 0
            self.currentNumValidResults = 0
            newspaperCode = self.newspaperDictionary[newspaper]
            newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
            hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, self.startRecordForGallicaQuery)
            numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
            while numberResultsForNewspaper > self.currentProcessedResults:
                self.sendQuery(newspaperQuery)
                if len(self.collectedQueries) >= self.recordNumber:
                    reachedLimit = True
                    break
                HuntOverseer.reportProgress(len(self.collectedQueries), self.recordNumber, "retrieving results")

            if reachedLimit:
                break


    def runLimitednoDictSearch(self):
        theBigQuery = self.baseQuery
        reachedLimit = False
        hunterForTotalNumberOfQueryResults = GallicaHunter(theBigQuery, self.startRecordForGallicaQuery)
        numberResultsForQuery = hunterForTotalNumberOfQueryResults.establishTotalHits(theBigQuery, False)
        while (numberResultsForQuery > self.currentProcessedResults) and not reachedLimit:
            self.sendQuery(theBigQuery)
            if len(self.collectedQueries) >= self.recordNumber:
                reachedLimit = True

    def runUnlimitednoDictSearch(self):
        theBigQuery = self.baseQuery
        hunterForTotalNumberOfQueryResults = GallicaHunter(theBigQuery, self.startRecordForGallicaQuery)
        numberResultsForQuery = hunterForTotalNumberOfQueryResults.establishTotalHits(theBigQuery, False)
        while numberResultsForQuery > self.currentProcessedResults:
            self.sendQuery(theBigQuery)


    def sendQuery(self, queryToSend):
        hunter = GallicaHunter(queryToSend, self.startRecordForGallicaQuery)
        hunter.hunt()
        results = hunter.getResultList()
        self.currentNumPurgedResults = hunter.getNumberPurgedResults()
        self.currentProcessedResults = self.currentProcessedResults + len(results) + self.currentNumPurgedResults
        self.currentNumValidResults = self.currentProcessedResults - self.currentNumPurgedResults
        self.collectedQueries = self.collectedQueries + results
        self.startRecordForGallicaQuery = self.startRecordForGallicaQuery + 50


    def packageQuery(self):
        filePacker = GallicaPackager(self.searchTerm, self.newspaper, self.collectedQueries,
                                     [self.lowYear, self.highYear])
        filePacker.makeCSVFile()
        filePacker.makeGraph()

    def establishNumberQueries(self):
        if type(self.recordNumber) is int:
            self.numberQueriesToGallica = self.recordNumber // 50

    def printTopTenPapers(self):
        def newsCountSort(theList):
            return theList[1]

        self.topPapers.sort(key=newsCountSort, reverse=True)
        print()
        for i in range(10):
            newspaper = self.topPapers[i][0]
            count = self.topPapers[i][1]
            place = i + 1
            line = "{place}. {newspaper}, {count}".format(place=place, newspaper=newspaper, count=count)
            print(line)


    def findTotalResultsForUnlimitedNewspaperSearch(self):
        toBeDeleted = []
        progressMeter = 0
        for newspaper in self.newspaperDictionary:
            progressMeter = progressMeter + 1
            HuntOverseer.reportProgress(progressMeter, len(self.newspaperDictionary), "finding total results")
            newspaperCode = self.newspaperDictionary[newspaper]
            newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
            hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, self.startRecordForGallicaQuery)
            numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
            if numberResultsForNewspaper == 0:
                toBeDeleted.append(newspaper)
            else:
                self.numResultsForEachPaper.update({newspaper : numberResultsForNewspaper})
                self.totalResults = self.totalResults + numberResultsForNewspaper
        for uselessPaper in toBeDeleted:
            self.newspaperDictionary.pop(uselessPaper)

    @staticmethod
    def reportProgress(iteration, total, part):
        progress = str(((iteration / total) * 100))
        print("{0}% complete {1}          ".format(progress[0:5], part),end="\r")
        sys.stdout.flush()
        if iteration == total:
            print()




