from gallicaHunter import GallicaHunter
from gallicaPaperFinder import GallicaPaperFinder
from huntOverseer import HuntOverseer
from gallicaGrapher import GallicaGrapher
from multipleSearchTermHunt import MultipleSearchTermHunt

import sys


def main():
	# Put this into another method eventually and get rid of confusing references to sys.argv
	if len(sys.argv) == 1:
		paperFinder = GallicaPaperFinder("1777-1950")
		paperFinder.findPapersOnGallica()
	else:
		unSplitSearchItem = sys.argv[1]
		searchItems = unSplitSearchItem.split("~")
		if len(sys.argv) == 5:
			graphType = sys.argv[2]
			uniqueGraphs = sys.argv[3]
			samePage = sys.argv[4]
			if searchItems[0][len(searchItems[0]) - 3: len(searchItems[0])] == "csv":
				settingDict = {"graphType":graphType,
								"uniqueGraphs":uniqueGraphs,
								"samePage":samePage}
				csvPackager = GallicaGrapher(searchItems[0], None, settingDict)
				csvPackager.parseGraphSettings()
				csvPackager.plotGraphAndMakePNG()
		else:
			newspaper = sys.argv[2]
			yearRange = sys.argv[3]
			strictYearRange = sys.argv[4]
			graphType = sys.argv[5]
			uniqueGraphs = sys.argv[6]
			samePage = sys.argv[7]
			if len(sys.argv) == 9:
				recordNumber = sys.argv[8]
			else:
				recordNumber = 0
			requestToRun = MultipleSearchTermHunt(searchItems, newspaper, yearRange, strictYearRange,
												  recordNumber=recordNumber,
												  graphType=graphType,
												  uniqueGraphs=uniqueGraphs,
												  samePage=samePage)
			requestToRun.runMultiTermQuery()


main()
