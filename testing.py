# from sys import stdin
# from multiprocessing import Pool, Array, Process, Manager
# import csv
# from gallicaHunter import GallicaHunter
#
#
# def makeBetterNames(row):
# 	currentLine = row
# 	priorName = currentLine[0]
# 	newspaperCode = currentLine[4]
# 	query = 'arkPress all "{newsKey}" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending' \
# 		.format(newsKey=newspaperCode, searchWord="e")
# 	name = GallicaHunter.establishName(query, priorName)
# 	currentLine[0] = name
# 	print(currentLine)
# 	return currentLine
#
# #Clean the csv first... gotta git rid of funky "
# # def addIndex():
# # 	with open("CleanDates Journals 1777-1950.csv", "r") as inFile:
# # 		reader = csv.reader(inFile, quotechar=None)
# # 		with open("Journals 1777-1950.csv", "w") as outFile:
# # 			writer = csv.writer(outFile)
# # 			print(writer.dialect)
# # 			i = 1
# # 			next(reader)
# # 			for row in reader:
# # 				currentLine = row
# # 				currentLine
# # 				currentLine.append(i)
# # 				writer.writerow(currentLine)
# # 				i = i + 1
# # 			print(i)
#
#
#
#
# if __name__ == '__main__':
# 	# addIndex()
#
# 	with Manager() as toShare:
# 		theList = toShare.list()
# 		with open("Journals 1777-1950.csv", "r", encoding="utf8") as inFile:
# 			reader = csv.reader(inFile, quotechar='"', delimiter=",", quoting=csv.QUOTE_ALL, skipinitialspace=True)
# 			with open("AvailableJournals 1777-1950.csv", "w", encoding="utf8") as outFile:
# 				writer = csv.writer(outFile, quotechar='"', delimiter=",", quoting=csv.QUOTE_ALL, skipinitialspace=True)
# 				next(reader)
# 				with Pool(10) as pool:
# 					theList.append(pool.map(makeBetterNames, reader))
# 				for entry in theList[0]:
# 					entry[0] = entry[0].replace('"', '')
# 					writer.writerow(entry)
