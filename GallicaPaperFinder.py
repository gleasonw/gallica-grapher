import requests
import pathlib
import re
from lxml import etree

class GallicaPaperFinder:
    def __init__(self, yearRange):
        self.yearRange = []
        self.query = ''
        self.journalIdentifierResults = []
        self.queryHitNumber = 0
        self.totalHits = 0
        self.determineYearRange(yearRange)
        self.determineQuery()
        self.determineTotalHits()

    def findPapersOnGallica(self):
        startRecord = 0
        numberQueriesToGallica = 200
        for j in range(numberQueriesToGallica):

            self.progressReporter(startRecord)

            parameters = {"version": 1.2, "operation": "searchRetrieve","collapsing": "true", "exactSearch": "false", "query" : self.query, "startRecord" : startRecord, "maximumRecords" : 50}
            response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)

            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                print(response.url)
                numberQueriesToGallica = numberQueriesToGallica + 1
                continue

            endedEarly = self.paperListCreator(root)
            if endedEarly:
                break
            else:
                startRecord = startRecord + 51

        self.makeCSVofJournals()

    def paperListCreator(self, targetXMLroot):
        abortCheck = False
        for queryHit in targetXMLroot.iter("{http://www.loc.gov/zing/srw/}record"):

            self.queryHitNumber = self.queryHitNumber + 1

            extraDataForOCRquality = queryHit[5]
            likelihoodOfTextMode = extraDataForOCRquality[3].text
            if float(likelihoodOfTextMode) < 60:
                continue

            data = queryHit[2][0]
            journalOfHit = '"' + data.find('{http://purl.org/dc/elements/1.1/}title').text + '"'
            identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
            publishDate = data.find('{http://purl.org/dc/elements/1.1/}date').text

            nineDigitCode = identifierOfHit[len(identifierOfHit)-16:len(identifierOfHit)-5]
            newspaperCode = nineDigitCode + "_date"

            try:
                fullResult = journalOfHit + ", " + publishDate + ", " + likelihoodOfTextMode + ", " + identifierOfHit + ", " + newspaperCode
            except TypeError:
                raise
                print(journalOfHit, identifierOfHit, publishDate)
                continue

            self.journalIdentifierResults.append(fullResult)

            if self.queryHitNumber == self.totalHits:
                abortCheck = True
                return(abortCheck)

        return(abortCheck)


    def makeCSVofJournals(self):
        lowerYear = self.yearRange[0]
        higherYear = self.yearRange[1]
        fileName = "Journals " + lowerYear + "-" + higherYear + ".csv"
        outFile = open(fileName, "w",encoding="utf8")
        outFile.write("journal,publishDate,textQuality,url,code \n")
        for csvEntry in self.journalIdentifierResults:
            outFile.write(csvEntry + "\n")
        outFile.close()


    def determineYearRange(self, yearRange):
        twoYearsInAList = re.split(r'[;,\-\s*]', yearRange)
        self.yearRange = twoYearsInAList

    def determineTotalHits(self):
        counterToEnsureSuccess = 1
        for j in range(counterToEnsureSuccess):
            parameters = {"version": 1.2, "operation": "searchRetrieve","collapsing": "true", "exactSearch": "false", "query" : self.query, "startRecord" : 0, "maximumRecords" : 1}
            response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)
            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                print(response.url)
                counterToEnsureSuccess = counterToEnsureSuccess + 1
                continue

        self.totalHits = int(root[2].text)

    def determineQuery(self):
        lowerYear = self.yearRange[0]
        higherYear = self.yearRange[1]
        query = ('(ocrquality >= "060.00") and '
                '(dc.language all "fre") and '
                '(dc.type all "fascicule") and '
                '(gallicapublication_date >= "{firstYear}" and '
                'gallicapublication_date <= "{secondYear}") '
                'sortby dc.date/sort.ascending')
        query = query.format(firstYear = lowerYear, secondYear = higherYear)
        self.query = query

    def makeDictionary():
        pass

    def progressReporter(self, currentSpot):
        progress = str(((currentSpot / self.totalHits) * 100))
        progressWith4Digits = progress[0:4]
        print(progressWith4Digits + "% complete")
