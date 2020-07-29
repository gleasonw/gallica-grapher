from gallicaHunter import GallicaHunter
from gallicaPaperFinder import GallicaPaperFinder
from huntOverseer import HuntOverseer

import sys

def main():
	#Put this into another method eventually
	if len(sys.argv) == 1:
		paperFinder = GallicaPaperFinder("1777-1950")
		paperFinder.findPapersOnGallica()
	else:
		try:
			requestToRun = HuntOverseer(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
		except:
			print("***Usage: python gallicaMainDriver searchTerm recordNumber newspaper yearRange***")
			raise

main()

"""
cb32757974m_date
cb34431794k_date
cb32858360p_date
cb39294634r_date
cb32895690j_date

"""
