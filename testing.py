from sys import stdin
from multiprocessing import Pool, Array, Process
import csv
from gallicaHunter import GallicaHunter


# def makeBetterNames(row):
# 	print(row)
# 	currentLine = row
# 	newspaperCode = currentLine[4]
# 	query = 'arkPress all "{newsKey}" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending' \
# 		.format(newsKey=newspaperCode, searchWord="e")
# 	name = GallicaHunter.establishName(query)
# 	currentLine[0] = name
# 	toShare currentLine

def addIndex():
	with open("CleanDates Journals 1777-1950.csv", "r") as inFile:
		reader = csv.reader(inFile, quotechar=None)
		with open("Journals 1777-1950.csv", "w") as outFile:
			writer = csv.writer(outFile)
			print(writer.dialect)
			i = 1
			next(reader)
			for row in reader:
				currentLine = row
				currentLine
				currentLine.append(i)
				writer.writerow(currentLine)
				i = i + 1
			print(i)




if __name__ == '__main__':
	addIndex()

	# toShare = Array('c', 6000, lock=False)
	# with open("CleanDates Journals 1777-1950.csv", "r", encoding="utf8") as inFile:
	# 	reader = csv.reader(inFile)
	# 	with open("Journals 1777-1950.csv", "w", encoding="utf8") as outFile:
	# 		writer = csv.writer(outFile)
	# 		maxLength = 0
	# 		with Pool(10) as pool:
	# 			pool.map(makeBetterNames, reader)
	# 		for newPaper in toShare:
	# 			writer.writerow(newPaper)
