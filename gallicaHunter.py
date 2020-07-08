import requests
import pathlib
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
	def __init__(self):
		pass
		

	"""
	params: 
	
	searchTerm = the term you're retrieving from Gallica
	recordNumber = the number of records you desire
	newspaperKey = the gallica key of the newspaper you desire
	
	"""
	def hunt(self, searchTerm, recordNumber, newspaperKey):
	
		#query run (recordNumber floor-divided by 50) times because of query size limit of 50
		startRecord = 0
		journalDateIdentifierList = []
		numberQueries = recordNumber // 50
		
		for j in range(numberQueries):
			parameters = {"version": 1.2, "operation": "searchRetrieve", "query" :'arkPress all "%s" and (gallica all "%s") sortby dc.date/sort.ascending' % (newspaperKey, searchTerm), "startRecord" : startRecord, "maximumRecords" : 50, "collapsing" : "disabled"}
			response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)
			root = etree.fromstring(response.content)
			
			# Format everything for eventual csv copy
			startJournalDateIdentifierList = len(journalDateIdentifierList)
			
			# Go through XML, add all journal titles (all entries). Then go through dates, adding to index incrementally (date in same order as title). Ditto for identifier.
			for child in root.iter("{http://purl.org/dc/elements/1.1/}title"):
				journalTitle = child.text
				journalDateIdentifierList.append(journalTitle)
			i = startJournalDateIdentifierList
			for child in root.iter("{http://purl.org/dc/elements/1.1/}date"):
				journalDate = child.text
				journalTitle = journalDateIdentifierList[i]
				journalTitleDate = "{0}, {1}".format(journalTitle, journalDate)
				journalDateIdentifierList[i] = journalTitleDate
				i = i + 1
			i = startJournalDateIdentifierList
			for child in root.iter("{http://purl.org/dc/elements/1.1/}identifier"):
				journalTitleDate = journalDateIdentifierList[i]
				journalIdentifierUrl = child.text
				journalTitleDateIdentifier = "{0}, {1}".format(journalTitleDate, journalIdentifierUrl)
				journalDateIdentifierList[i] = journalTitleDateIdentifier
				i = i + 1
			startRecord = startRecord + 51
		
		#making the file
		wordsInTitle = journalTitle[0:5]
		wordsInQuery = searchTerm.split(" ")
		fileName = ''
		fileName = fileName + wordsInTitle
		fileName = fileName + "--"
		for word in wordsInQuery:
			fileName = fileName + word
		fileName = fileName + ".csv"
		outFile = open(fileName, "w")
		outFile.write("journal,date,url\n")
		for csvEntry in journalDateIdentifierList:
			outFile.write(csvEntry + "\n")
		outFile.close()
	
	def huntBigSix(self, searchTerm):
	
		newspapers=["lepetitjournal","lefigaro","letemps","journaldesdebats","lexixesiecle","lepetitparisien"]
		journalDateIdentifierList = []
		
		for p in range(6):
			newspaperName = newspapers[p]
			newspaperDictionary = GallicaHunter.newspaperDict
			newspaperKey = newspaperDictionary.get(newspaperName)
			startRecord = 0
			numberQueries = 10
			
			for j in range(numberQueries):
				parameters = {"version": 1.2, "operation": "searchRetrieve", "query" :'arkPress all "%s" and (gallica all "%s") sortby dc.date/sort.ascending' % (newspaperKey, searchTerm), "startRecord" : startRecord, "maximumRecords" : 50, "collapsing" : "disabled"}
				response = requests.get("https://gallica.bnf.fr/SRU",params=parameters)
				root = etree.fromstring(response.content)
				
				# Format everything for eventual csv copy
				startJournalDateIdentifierList = len(journalDateIdentifierList)
				
				# Go through XML, add all journal titles (all entries). Then go through dates, adding to index incrementally (date in same order as title). Ditto for identifier.
				for child in root.iter("{http://purl.org/dc/elements/1.1/}title"):
					journalTitle = child.text
					journalDateIdentifierList.append(journalTitle)
				i = startJournalDateIdentifierList
				for child in root.iter("{http://purl.org/dc/elements/1.1/}date"):
					journalDate = child.text
					journalTitle = journalDateIdentifierList[i]
					journalTitleDate = "{0}, {1}".format(journalTitle, journalDate)
					journalDateIdentifierList[i] = journalTitleDate
					i = i + 1
				i = startJournalDateIdentifierList
				for child in root.iter("{http://purl.org/dc/elements/1.1/}identifier"):
					journalTitleDate = journalDateIdentifierList[i]
					journalIdentifierUrl = child.text
					journalTitleDateIdentifier = "{0}, {1}".format(journalTitleDate, journalIdentifierUrl)
					journalDateIdentifierList[i] = journalTitleDateIdentifier
					i = i + 1
				startRecord = startRecord + 51
			
		#making the file
		wordsInQuery = searchTerm.split(" ")
		fileName = "BigSix--"
		for word in wordsInQuery:
			fileName = fileName + word
		fileName = fileName + ".csv"
		outFile = open(fileName, "w")
		outFile.write("journal,date,url\n")
		for csvEntry in journalDateIdentifierList:
			articles = csvEntry.split(",")
			print(articles)
			year = int(articles[1][0:4])
			if year >= 1875 and year <= 1920:
				outFile.write(csvEntry + "\n")
		outFile.close()
			
			