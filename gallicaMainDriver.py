from gallicaHunter import GallicaHunter
from gallicaPaperFinder import GallicaPaperFinder
from huntOverseer import HuntOverseer
from gallicaGrapher import GallicaGrapher
from multipleSearchTermHunt import MultipleSearchTermHunt

import sys


def main():
	# Put this into another method eventually and get rid of confusing references to sys.argv
	unSplitSearchItem = sys.argv[1]
	searchItems = unSplitSearchItem.split(".")
	newspaper = sys.argv[2]
	yearRange = sys.argv[3]
	strictYearRange = sys.argv[4]
	graphType = sys.argv[5]
	numberGraphs = sys.argv[6]
	recordNumber = sys.argv[7]
	if len(sys.argv) == 1:
		paperFinder = GallicaPaperFinder("1777-1950")
		paperFinder.findPapersOnGallica()
	elif len(sys.argv) == 2:
		if searchItems[0][len(searchItems[0]) - 3: len(searchItems[0])] == "csv":
			csvPackager = GallicaGrapher(searchItems[0], None)
			csvPackager.makeGraph()
	else:
		requestToRun = MultipleSearchTermHunt(searchItems, newspaper, yearRange, strictYearRange,
											  recordNumber=recordNumber,
											  graphType=graphType,
											  numberGraphs=numberGraphs)
		requestToRun.runMultiTermQuery()


main()
