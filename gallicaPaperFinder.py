import requests
import pathlib
import re
import csv
from lxml import etree


class GallicaPaperFinder:
    def __init__(self, yearRange):
        self.yearRange = []
        self.query = ''
        self.journalIdentifierResults = []
        self.queryHitNumber = 0
        self.totalHits = 0
        self.reachEndOfResults = False
        self.determineYearRange(yearRange)
        self.determineQuery()
        self.determineTotalHits()

    def findPapersOnGallica(self):
        startRecord = 0
        numberQueriesToGallica = 200
        for j in range(numberQueriesToGallica):

            self.progressReporter()

            parameters = {"version": 1.2, "operation": "searchRetrieve","collapsing": "true", "exactSearch": "false", "query" : self.query, "startRecord" : startRecord, "maximumRecords" : 50}
            response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)

            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                print(response.url)
                numberQueriesToGallica = numberQueriesToGallica + 1
                continue

            self.paperListCreator(root)
            if self.reachEndOfResults:
                break
            else:
                startRecord = startRecord + 51

        self.makeCSVofJournals()
        self.makeCSVwithCleanDates()

    def paperListCreator(self, targetXMLroot):
        for queryHit in targetXMLroot.iter("{http://www.loc.gov/zing/srw/}record"):

            self.queryHitNumber = self.queryHitNumber + 1
            if self.queryHitNumber > self.totalHits:
                self.reachEndOfResults = True
                return

            extraDataForOCRquality = queryHit[5]
            likelihoodOfTextMode = extraDataForOCRquality[3].text
            if float(likelihoodOfTextMode) < 60:
                continue

            data = queryHit[2][0]
            try:
                journalOfHit = '"' + data.find('{http://purl.org/dc/elements/1.1/}title').text + '"'
                identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
                publishDate = data.find('{http://purl.org/dc/elements/1.1/}date').text
                nineDigitCode = identifierOfHit[len(identifierOfHit) - 16:len(identifierOfHit) - 5]
                newspaperCode = nineDigitCode + "_date"
            except AttributeError:
                print("that's a funky result.\n")
                etree.dump(targetXMLroot)
                continue
            try:
                fullResult = journalOfHit + ", " + publishDate + ", " + likelihoodOfTextMode + ", " + identifierOfHit + ", " + newspaperCode
            except TypeError:
                print("****AHHHHHHH type error ****\n")
                print(journalOfHit, identifierOfHit, publishDate)
                continue

            self.journalIdentifierResults.append(fullResult)

    # Change to csv python
    def makeCSVofJournals(self):
        lowerYear = self.yearRange[0]
        higherYear = self.yearRange[1]
        fileName = "Journals " + lowerYear + "-" + higherYear + ".csv"
        outFile = open(fileName, "w", encoding="utf8")
        outFile.write("journal,publishDate,textQuality,url,code \n")
        for csvEntry in self.journalIdentifierResults:
            outFile.write(csvEntry + "\n")
        outFile.close()

    def makeCSVwithCleanDates(self):
        lowerYear = self.yearRange[0]
        higherYear = self.yearRange[1]
        fileName = "CleanDates Journals " + higherYear + "-" + lowerYear + ".csv"
        with open("Journals 1777-1950.csv", "r", encoding="utf8") as inFile:
            reader = csv.reader(inFile)
            next(reader)
            with open(fileName, "w", encoding="utf8") as outFile:
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
        outFile.close()
        inFile.close()

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

    def determineTotalHits(self):
        counterToEnsureSuccess = 1
        for j in range(counterToEnsureSuccess):
            parameters = dict(version=1.2, operation="searchRetrieve", collapsing="true", exactSearch="false",
                              query=self.query, startRecord=0, maximumRecords=1)
            response = requests.get("https://gallica.bnf.fr/SRU", params=parameters)
            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                print(response.url)
                counterToEnsureSuccess = counterToEnsureSuccess + 1
                continue
        self.totalHits = int(root[2].text)
