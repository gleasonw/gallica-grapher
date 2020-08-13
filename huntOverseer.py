import csv
import math
import re
import sys
import shutil
import os

from gallicaHunter import GallicaHunter

from gallicaPackager import GallicaPackager
from unlimitedOverseerofNewspaperHunt import UnlimitedOverseerOfNewspaperHunt
from limitedOverseerofNewspaperHunt import LimitedOverseerOfNewspaperHunt


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
        self.topTenPapers = []
        self.numResultsForEachPaper = {}
        self.fileName = ''

        self.establishRecordNumber(args)
        self.establishStrictness(args[3])
        self.establishYearRange(args[2])
        self.parseNewspaperDictionary()
        self.buildQuery()

    def runQuery(self):
        self.initiateQuery()

    def establishRecordNumber(self, argList):
        if len(argList) == 5:
            self.recordNumber = int(argList[4])

    @staticmethod
    def sendQuery(queryToSend, startRecord, numRecords):
        hunter = GallicaHunter(queryToSend, startRecord, numRecords)
        hunter.hunt()
        return hunter


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
                self.findTotalResultsForUnlimitedNewspaperSearch()
                self.runLimitedSearchOnDictionary()
            else:
                self.findTotalResultsForUnlimitedNewspaperSearch()
                self.runUnlimitedSearchOnDictionary()
        self.packageQuery()

    def runUnlimitedSearchOnDictionary(self):
        progress = 0
        for newspaper in self.newspaperDictionary:
            numberResultsInPaper = self.numResultsForEachPaper[newspaper]
            newspaperCode = self.newspaperDictionary[newspaper]
            newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
            newspaperHuntOverseer = UnlimitedOverseerOfNewspaperHunt(newspaperQuery, numberResultsInPaper)
            newspaperHuntOverseer.scourPaper()
            self.collectedQueries = self.collectedQueries + newspaperHuntOverseer.getResultList()
            progress = progress + numberResultsInPaper
            HuntOverseer.reportProgress(progress, self.totalResults, "retrieving results")
            self.numResultsForEachPaper.update({newspaper: newspaperHuntOverseer.getNumberValidResults()})

    def runLimitedSearchOnDictionary(self):
        totalNumberValidResults = 0
        resultsLeftToGet = self.recordNumber
        for newspaper in self.newspaperDictionary:
            numberResultsInPaper = self.numResultsForEachPaper[newspaper]
            newspaperCode = self.newspaperDictionary[newspaper]
            newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
            numberResultsWanted = min(resultsLeftToGet, numberResultsInPaper)
            newspaperHuntOverseer = LimitedOverseerOfNewspaperHunt(newspaperQuery, numberResultsInPaper, numberResultsWanted)
            newspaperHuntOverseer.scourPaper()
            currentNumberValidResults = newspaperHuntOverseer.getNumberValidResults()
            #probably redundant
            if newspaperHuntOverseer.getNumberValidResults() == 0:
                break
            else:
                totalNumberValidResults = totalNumberValidResults + currentNumberValidResults
                if totalNumberValidResults > self.recordNumber:
                    break
            self.collectedQueries = self.collectedQueries + newspaperHuntOverseer.getResultList()
            resultsLeftToGet = resultsLeftToGet - currentNumberValidResults
            if resultsLeftToGet == 0:
                break

    def runLimitednoDictSearch(self):
        theBigQuery = self.baseQuery
        hunterForTotalNumberOfQueryResults = GallicaHunter(theBigQuery, 1, 1)
        numberResultsForQuery = hunterForTotalNumberOfQueryResults.establishTotalHits(theBigQuery, False)
        numProcessedResults = 0
        startRecord = 1
        maximumResults = min(numberResultsForQuery, self.recordNumber)
        while maximumResults > numProcessedResults:
            amountRemaining = self.recordNumber - numProcessedResults
            if amountRemaining >= 50:
                numRecords = 50
            else:
                numRecords = amountRemaining
            batchHunter = self.sendQuery(theBigQuery, startRecord, numRecords)
            startRecord = startRecord + 50
            results = batchHunter.getResultList()
            numPurged = batchHunter.getNumberPurgedResults()
            self.collectedQueries = self.collectedQueries + results
            numProcessedResults = numProcessedResults + len(results) + numPurged

    def runUnlimitednoDictSearch(self):
        theBigQuery = self.baseQuery
        hunterForTotalNumberOfQueryResults = GallicaHunter(theBigQuery, 1, 1)
        numberResultsForQuery = hunterForTotalNumberOfQueryResults.establishTotalHits(theBigQuery, False)
        numProcessedResults = 0
        startRecord = 1
        while numberResultsForQuery > numProcessedResults:
            batchHunter = self.sendQuery(theBigQuery, startRecord, 50)
            startRecord = startRecord + 50
            results = batchHunter.getResultList()
            numPurged = batchHunter.getNumberPurgedResults()
            self.collectedQueries = self.collectedQueries + results
            numProcessedResults = numProcessedResults + len(results) + numPurged

    #make list of newspapers with number results. Do at the end of all queries (since # results updated during lower level runs)

    def findTotalResultsForUnlimitedNewspaperSearch(self):
        toBeDeleted = []
        progressMeter = 0
        for newspaper in self.newspaperDictionary:
            progressMeter = progressMeter + 1
            HuntOverseer.reportProgress(progressMeter, len(self.newspaperDictionary), "finding total results")
            newspaperCode = self.newspaperDictionary[newspaper]
            newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
            hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, 1, 1)
            numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
            self.totalResults = self.totalResults + numberResultsForNewspaper
            if numberResultsForNewspaper == 0:
                toBeDeleted.append(newspaper)
            else:
                self.numResultsForEachPaper.update({newspaper: numberResultsForNewspaper})
        for uselessPaper in toBeDeleted:
            self.newspaperDictionary.pop(uselessPaper)

    def findTotalResultsForLimitedNewspaperSearch(self):
        toBeSaved = []
        progressMeter = 0
        for newspaper in self.newspaperDictionary:
            progressMeter = progressMeter + 1
            HuntOverseer.reportProgress(progressMeter, len(self.newspaperDictionary), "finding total results")
            newspaperCode = self.newspaperDictionary[newspaper]
            newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
            hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, 1, 1)
            numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
            self.totalResults = self.totalResults + numberResultsForNewspaper
            if self.totalResults >= self.recordNumber:
                break
            elif numberResultsForNewspaper != 0:
                self.numResultsForEachPaper.update({newspaper: numberResultsForNewspaper})
        for newspaper in self.newspaperDictionary:
            if newspaper not in toBeSaved:
                uselessPaper = newspaper
                self.newspaperDictionary.pop(uselessPaper)

    def packageQuery(self):
        self.makeCSVFile()
        self.printTopTenPapers()
        filePacker = GallicaPackager(self.fileName, self.topTenPapers)
        filePacker.makeGraph()

    def establishNumberQueries(self):
        if type(self.recordNumber) is int:
            self.numberQueriesToGallica = self.recordNumber // 50


    def printTopTenPapers(self):
        def newsCountSort(theList):
            return theList[1]

        for newspaper in self.newspaperDictionary:
            numResults = self.newspaperDictionary[newspaper]
            self.topPapers.append([newspaper, numResults])

        self.topPapers.sort(key=newsCountSort, reverse=True)
        print()

        for i in range(10):
            newspaper = self.topPapers[i][0]
            self.topTenPapers.append(newspaper)
            count = self.topPapers[i][1]
            place = i + 1
            line = "{place}. {newspaper} ({count})".format(place=place, newspaper=newspaper, count=count)
            print(line)

        dictionaryFile = "{0}-{1}".format("TopPaperDict", self.fileName)

        with open(os.path.join("./CSVdata", dictionaryFile), "w", encoding="utf8") as outFile:
            writer = csv.writer(outFile)
            for newspaper in self.topTenPapers:
                writer.writerow(newspaper)

    def makeCSVFile(self):
        self.fileName = self.determineFileName()
        with open(self.fileName, "w", encoding="utf8") as outFile:
            writer = csv.writer(outFile)
            writer.writerow(["date", "journal", "url"])
            for csvEntry in self.collectedQueries:
                writer.writerow(csvEntry)
        shutil.move(os.path.join("./", self.fileName),os.path.join("./CSVdata", self.fileName))

    def determineFileName(self):
        if self.newspaper == "all":
            nameOfFile = self.searchTerm + "-all-"
        else:
            nameOfFile = self.newspaper + "-"
            wordsInQuery = self.searchTerm.split(" ")
            for word in wordsInQuery:
                nameOfFile = nameOfFile + word
        if self.isYearRange:
            nameOfFile = nameOfFile + str(self.lowYear) + "." + str(self.highYear)
        nameOfFile = nameOfFile + ".csv"
        return nameOfFile

    @staticmethod
    def reportProgress(iteration, total, part):
        progress = str(((iteration / total) * 100))
        print("{0}% complete {1}          ".format(progress[0:5], part),end="\r")
        sys.stdout.flush()
        if iteration == total:
            print()




