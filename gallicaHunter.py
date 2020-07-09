import requests
import pathlib
import os
from lxml import etree
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
	def __init__(self, searchTerm, recordNumber, newspaper):
		self.searchTerm = searchTerm
		self.recordNumber = recordNumber
		self.journalDateIdentifierResults = []
		self.newspaperDictionary = establishNewspaperDictionary(newspaper)

	"""
	params:

	searchTerm = the term you're retrieving from Gallica
	recordNumber = the number of records you desire
	newspaperKey = the gallica key of the newspaper you desire

	"""
	def hunt(self):
		#Add something to restrict year range if wanted
		for newspaper in newspaperDictionary:
			newspaperKey = newspaperDictionary[newspaper]
			startRecord = 0
			numberQueriesToGallica = 10

			for j in range(numberQueriesToGallica):
				parameters = {"version": 1.2, "operation": "searchRetrieve", "query" :'arkPress all "%s" and (gallica all "%s") sortby dc.date/sort.ascending' % (newspaperKey, self.searchTerm), "startRecord" : startRecord, "maximumRecords" : 50, "collapsing" : "disabled"}
				response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)
				root = etree.fromstring(response.content)

				# Format everything for eventual csv copy
				startOfResultsList = len(self.journalDateIdentifierResults)

				# Go through XML, add all journal titles (all entries). Then go through dates, adding to index incrementally (date in same order as title). Ditto for identifier.
				for child in root.iter("{http://purl.org/dc/elements/1.1/}title"):
					journalTitle = child.text
					self.journalDateIdentifierResults.append(journalTitle)
				i = startOfResultsList
				for child in root.iter("{http://purl.org/dc/elements/1.1/}date"):
					journalDate = child.text
					journalTitle = self.journalDateIdentifierResults[i]
					journalTitleDate = "{0}, {1}".format(journalTitle, journalDate)
					self.journalDateIdentifierResults[i] = journalTitleDate
					i = i + 1
				i = startOfResultsList
				for child in root.iter("{http://purl.org/dc/elements/1.1/}identifier"):
					journalTitleDate = self.journalDateIdentifierResults[i]
					journalIdentifier = child.text
					journalTitleDateIdentifier = "{0}, {1}".format(journalTitleDate, journalIdentifier)
					self.journalDateIdentifierResults[i] = journalTitleDateIdentifier
					i = i + 1
				startRecord = startRecord + 51

		makeCSVFile()

	def establishNewspaperDictionary(self,newspaper):
		fullNewspaperDictionary = GallicaHunter.newspaperDict
		if newspaper is None:
			return(fullNewspaperDictionary)
		else:
			trimmedDictionary = {newspaper : fullNewspaperDictionary[newspaper]}
			return(trimmedDictionary)

	def makeCSVFile(self):
		fileName = determineFileName()
		outFile = open(fileName, "w")
		outFile.write("journal,date,url\n")
		for csvEntry in self.journalDateIdentifierResults:
			outFile.write(csvEntry + "\n")
		outFile.close()

	def determineFileName(self):
		if self.newspaper is None:
			nameOfFile = "AllNewspapers--"
		else:
			nameOfFile = self.newspaper + "--"
		wordsInQuery = self.searchTerm.split(" ")
		for word in wordsInQuery:
			nameOfFile = nameOfFile + word
		return(nameOfFile)
