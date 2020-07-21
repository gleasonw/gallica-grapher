import requests
import pathlib
import re
from lxml import etree
from gallicaPackager import GallicaPackager

class GallicaHunter:

    def __init__(self, searchTerm, recordNumber, newspaper, yearRange):
        self.searchTerm = searchTerm
        self.recordNumber = recordNumber
        self.dateJournalIdentifierResults = []
        self.newspaper = newspaper
        self.yearRange = []
        self.numberQueriesToGallica = 10
        self.query = ''
        self.establishYearRange(yearRange)
        self.establishNewspaperDictionary()
        self.establishNumberQueries(recordNumber)
        self.establishQuery()

    """
    params:

    searchTerm = the term you're retrieving from Gallica
    recordNumber = the number of records you desire
    newspaperKey = the gallica key of the newspaper you desire

    """
    def initiateQuery(self):
        if self.newspaper == "all":
            self.hunt()
        else:
            self.huntSomePapers()

        #move to master class
        filePacker = GallicaPackager(self.searchTerm, self.newspaper, self.dateJournalIdentifierResults, self.yearRange)
        filePacker.makeCSVFile()
        filePacker.makeGraph()

    def huntSomePapers(self):
        for newspaper in self.newspaperDictionary:
            newspaperKey = self.newspaperDictionary[newspaper]
            self.query = self.query.format(newsKey = newspaperKey)
            self.hunt()

    def hunt(self):
        startRecord = 0
        for j in range(self.numberQueriesToGallica):

            #make this a master class function
            progress = str(int((startRecord / (numberQueriesToGallica * 50)) * 100)) + "% complete"
            print(progress)
            
            parameters = {"version": 1.2, "operation": "searchRetrieve", "collapsing":"false","query" : self.query, "startRecord" : startRecord, "maximumRecords" : 50}
            response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)
            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                print(response.url)
                self.numberQueriesToGallica = self.numberQueriesToGallica + 1
                continue
            for queryHit in root.iter("{http://www.loc.gov/zing/srw/}record"):
                data = queryHit[2][0]
                dateOfHit = data.find('{http://purl.org/dc/elements/1.1/}date').text
                dateOfHit = self.standardizeDate(dateOfHit)
                journalOfHit = data.find('{http://purl.org/dc/elements/1.1/}title').text
                journalOfHit = re.sub(',', '', journalOfHit)
                identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
                try:
                    fullResult = dateOfHit + ", " + journalOfHit + ", " + identifierOfHit
                except TypeError:
                    print("****Something's up with this result.****")
                    print(dateOfHit, journalOfHit, identifierOfHit)
                    if dateOfHit is None:
                        dateOfHit = "NA"
                        try:
                            fullResult = dateOfHit + ", " + journalOfHit + ", " + identifierOfHit
                        except TypeError:
                            continue
                    else:
                        continue
                currentResults = self.dateJournalIdentifierResults
                currentResults.append(fullResult)

            startRecord = startRecord + 51

        print("\n ****Last record: " + str(startRecord) + "****\n")

    def establishNewspaperDictionary(self):
        if self.newspaper == "all":
            return
        elif self.newspaper == "bigsix":

            self.newspaperDictionary = fullNewspaperDictionary
        else:
            trimmedDictionary = {self.newspaper : fullNewspaperDictionary[self.newspaper]}
            self.newspaperDictionary = trimmedDictionary

    def establishYearRange(self, yearRange):
        self.yearRange = re.split(r'[;,\-\s*]', yearRange)

    def establishNumberQueries(self, recordNumber):
        if recordNumber is not None:
            self.numberQueriesToGallica = recordNumber // 50

    def establishQuery(self):
        if(len(self.yearRange) == 0):
            if self.newspaper == "all":
                self.query = '(gallica adj "{searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending'.format(searchWord = self.searchTerm)
            else:
                self.query = 'arkPress all "{{newsKey}}" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending'.format(searchWord = self.searchTerm)
        else:
            lowerYear = self.yearRange[0]
            higherYear = self.yearRange[1]
            if self.newspaper == "all":
                self.query = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and (gallica adj "{searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending'
            else:
                self.query = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{newsKey}}") and (gallica adj "{searchWord}")) sortby dc.date/sort.ascending'
            self.query = self.query.format(firstYear = lowerYear, secondYear = higherYear, searchWord = self.searchTerm)

    def standardizeDate(self, dateToStandardize):
        lengthOfDate = len(dateToStandardize)
        if lengthOfDate != 10:
            if lengthOfDate == 4:
                return(dateToStandardize + "-01-01")
            elif lengthOfDate == 7:
                return(dateToStandardize + "-01")
            elif lengthOfDate == 9:
                dates = dateToStandardize.split("-")
                lowerDate = int(dates[0])
                higherDate = int(dates[1])
                newDate = (lowerDate + higherDate) // 2
                return(str(newDate) + "-01-01")
        else:
            return(dateToStandardize)
