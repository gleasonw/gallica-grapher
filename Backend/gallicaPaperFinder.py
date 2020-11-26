import requests
import re
import csv
from lxml import etree
from Backend.gallica50BatchGetter import GallicaHunter

#Consider making a subclass of GallicaHunter
class GallicaPaperFinder():
    def __init__(self, yearRange):
        self.yearRange = []
        self.query = ''
        self.journalIdentifierResults = []
        self.queryHitNumber = 0
        self.totalHits = 0
        self.reachEndOfResults = False
        self.determineYearRange(yearRange)
        self.determineQuery()
        self.fileName = None
        self.totalHits = GallicaHunter.establishTotalHits(self.query)


    def findPapersOnGallica(self):
        startRecord = 0
        while self.queryHitNumber < self.totalHits:

            self.progressReporter()

            parameters = {"version": 1.2, "operation": "searchRetrieve","collapsing": "true", "exactSearch": "false", "query" : self.query, "startRecord" : startRecord, "maximumRecords" : 50}
            success = False
            while not success:
                try:
                    response = requests.get("https://gallica.bnf.fr/SRU", params=parameters)
                    root = etree.fromstring(response.content)
                    success = True
                except etree.XMLSyntaxError as e:
                    print("\n\n ****Gallica spat at you!**** \n")
                    print(response.url)

            self.paperListCreator(root)

        self.makeCSVofJournals()
        self.makeCSVwithCleanDates()

    def paperListCreator(self, targetXMLroot):
        for queryHit in targetXMLroot.iter("{http://www.loc.gov/zing/srw/}record"):

            self.queryHitNumber = self.queryHitNumber + 1

            extraDataForOCRquality = queryHit[5]
            likelihoodOfTextMode = extraDataForOCRquality[3].text
            if float(likelihoodOfTextMode) < 60:
                continue

            data = queryHit[2][0]
            try:
                journalOfHit = data.find('{http://purl.org/dc/elements/1.1/}title').text
                identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
                publishDate = data.find('{http://purl.org/dc/elements/1.1/}date').text
                nineDigitCode = identifierOfHit[len(identifierOfHit) - 16:len(identifierOfHit) - 5]
                newspaperCode = nineDigitCode + "_date"
            except AttributeError:
                print("that's a funky result.\n")
                etree.dump(targetXMLroot)
                continue
            fullResult = [journalOfHit, publishDate, likelihoodOfTextMode, identifierOfHit, newspaperCode]

            self.journalIdentifierResults.append(fullResult)

    def makeCSVofJournals(self):
        lowerYear = self.yearRange[0]
        higherYear = self.yearRange[1]
        self.fileName = "Journals " + lowerYear + "-" + higherYear + ".csv"
        with open(self.fileName, "w", encoding="utf8") as outFile:
            writer = csv.writer(outFile)
            writer.write(["journal","publishDate","textQuality","url","code"])
            for csvEntry in self.journalIdentifierResults:
                writer.write(csvEntry)

    def makeCSVwithCleanDates(self):
        lowerYear = self.yearRange[0]
        higherYear = self.yearRange[1]
        cleanFileName = "CleanDates Journals " + higherYear + "-" + lowerYear + ".csv"
        with open(self.fileName, "r", encoding="utf8") as inFile:
            reader = csv.reader(inFile)
            next(reader)
            with open(cleanFileName, "w", encoding="utf8") as outFile:
                writer = csv.writer(outFile)
                writer.writerow(["journal", "publishDate", "textQuality", "url", "code"])
                for newsData in reader:
                    publicationRange = newsData[1]
                    standardizedRange = self.standardizeDateRange(publicationRange)
                    if standardizedRange is None:
                        continue
                    else:
                        newsData[1] = standardizedRange
                        writer.writerow(newsData)

    def standardizeDateRange(self, dateRangeToStandardize):
        splitDates = dateRangeToStandardize.split("-")
        if len(splitDates) != 2:
            return None
        else:
            lowerDate = splitDates[0]
            lowerDate = lowerDate.replace(".", "9")
            lowerDate = lowerDate.replace("?", "9")
            higherDate = splitDates[1]
            higherDate = higherDate.replace(".", "0")
            higherDate = higherDate.replace("?", "0")

            try:
                INTlowerDate = int(lowerDate)
                INThigherDate = int(higherDate)
            except ValueError:
                return None

            if INTlowerDate >= INThigherDate:
                return None
            else:
                return (lowerDate + "-" + higherDate)

    def determineYearRange(self, yearRange):
        twoYearsInAList = re.split(r'[;,\-\s*]', yearRange)
        self.yearRange = twoYearsInAList

    def determineQuery(self):
        lowerYear = self.yearRange[0]
        higherYear = self.yearRange[1]
        query = ('(ocrquality >= "060.00") and '
                 '(dc.language all "fre") and '
                 '(dc.type all "fascicule") and '
                 '(gallicapublication_date >= "{firstYear}" and '
                 'gallicapublication_date <= "{secondYear}") '
                 'sortby dc.date/sort.ascending')
        query = query.format(firstYear=lowerYear, secondYear=higherYear)
        self.query = query

    def progressReporter(self):
        progress = str(((self.queryHitNumber / self.totalHits) * 100))
        progressWith4Digits = progress[0:4]
        print(progressWith4Digits + "% complete | ", self.queryHitNumber)