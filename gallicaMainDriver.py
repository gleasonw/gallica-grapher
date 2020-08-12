from gallicaHunter import GallicaHunter
from gallicaPaperFinder import GallicaPaperFinder
from huntOverseer import HuntOverseer
from gallicaPackager import GallicaPackager

import sys

def main():
    #Put this into another method eventually
    searchItem = sys.argv[1]
    if len(sys.argv) == 1:
        paperFinder = GallicaPaperFinder("1777-1950")
        paperFinder.findPapersOnGallica()
    elif len(sys.argv) == 2:
        if searchItem[len(searchItem)-3 : len(searchItem)] == "csv":
            csvPackager = GallicaPackager(searchItem, None)
            csvPackager.makeGraph()
    # elif type(searchItem) is list:
    #     requestToRun = MultipleSearchTermHunt(sys.argv[1], sys.argv[2], sys.argv[3],
    #                                         sys.argv[4])
    else:
        try:
            if len(sys.argv) == 6:
                requestToRun = HuntOverseer(sys.argv[1], sys.argv[2], sys.argv[3],
                                            sys.argv[4], sys.argv[5])
            else:
                requestToRun = HuntOverseer(sys.argv[1], sys.argv[2], sys.argv[3],
                                            sys.argv[4])
            requestToRun.runQuery()
        except:
            print("***Usage: python gallicaMainDriver searchTerm newspaper yearRange  strictYearRange? recordNumber***")
            raise
main()

"""
cb32757974m_date
cb34431794k_date
cb32858360p_date
cb39294634r_date
cb32895690j_date

"""
