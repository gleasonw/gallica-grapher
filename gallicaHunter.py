import requests
import pathlib
import re
from lxml import etree
from gallicaPackager import GallicaPackager

"""
tags for newspapers
petit journal = cb32895690j_date
"""

class GallicaHunter:
    newspaperDict = {
        "lepetitjournal": "cb32895690j_date",
        "lefigaro" : "cb34355551z_date",
        "letemps" : "cb34431794k_date",
        "journaldesdebats" : "cb39294634r_date",
        "lexixesiecle" : "cb32757974m_date",
        "lepetitparisien" : "cb34419111x_date"
    }
    def __init__(self, searchTerm, recordNumber, newspaper, yearRange):
        self.searchTerm = searchTerm
        self.recordNumber = recordNumber
        self.dateJournalIdentifierResults = []
        self.newspaper = ''
        self.yearRange = []
        self.numberQueriesToGallica = 10
        self.query = ''
        self.establishNewspaperDictionary(newspaper)
        self.establishYearRange(yearRange)
        self.establishNumberQueries(recordNumber)
        self.establishQuery()

    """
    params:

    searchTerm = the term you're retrieving from Gallica
    recordNumber = the number of records you desire
    newspaperKey = the gallica key of the newspaper you desire

    """
    def hunt(self):
        for newspaper in self.newspaperDictionary:
            newspaperKey = self.newspaperDictionary[newspaper]
            startRecord = 0
            for j in range(self.numberQueriesToGallica):
                queryWithProperPaper = self.query.format(newsKey = newspaperKey)
                parameters = {"version": 1.2, "operation": "searchRetrieve", "query" : queryWithProperPaper, "startRecord" : startRecord, "maximumRecords" : 50, "collapsing" : "disabled"}
                response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)
                root = etree.fromstring(response.content)
                for queryHit in root.iter("{http://www.loc.gov/zing/srw/}record"):
                    data = queryHit[2][0]
                    dateOfHit = data.find('{http://purl.org/dc/elements/1.1/}date').text
                    journalOfHit = data.find('{http://purl.org/dc/elements/1.1/}title').text
                    identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
                    fullResult = dateOfHit + ", " + journalOfHit + ", " + identifierOfHit
                    currentResults = self.dateJournalIdentifierResults
                    currentResults.append(fullResult)
                startRecord = startRecord + 51
            #run same but don't check the range each time

        filePacker = GallicaPackager(self.searchTerm, self.newspaper, self.dateJournalIdentifierResults, self.yearRange)
        filePacker.makeCSVFile()

    def establishNewspaperDictionary(self,newspaper):
        fullNewspaperDictionary = GallicaHunter.newspaperDict
        if (newspaper is None) or (newspaper == "all"):
            self.newspaperDictionary = fullNewspaperDictionary
        else:
            trimmedDictionary = {newspaper : fullNewspaperDictionary[newspaper]}
            self.newspaperDictionary = trimmedDictionary
            self.newspaper = newspaper

    def establishYearRange(self, yearRange):
        self.yearRange = re.split(r'[;,\-\s*]', yearRange)

    def establishNumberQueries(self, recordNumber):
        if recordNumber is not None:
            self.numberQueriesToGallica = recordNumber // 50

    def establishQuery(self):
        if(len(self.yearRange) == 0):
            self.query = 'arkPress all "{{newsKey}}" and (gallica all "{searchWord}") sortby dc.date/sort.ascending'.format(searchWord = self.searchTerm)
        else:
            lowerYear = self.yearRange[0]
            higherYear = self.yearRange[1]
            self.query = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{newsKey}}") and (gallica all "{searchWord}")) sortby dc.date/sort.ascending'.format(firstYear = lowerYear, secondYear = higherYear, searchWord = self.searchTerm)
