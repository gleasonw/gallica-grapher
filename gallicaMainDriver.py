from gallicaHunter import GallicaHunter
import sys

def main():
	if len(sys.argv) == 2:
		try:
			allPaperHunter = GallicaHunter(sys.argv[1])
			allPaperHunter.hunt()
		# Change this eventually
		except:
			print("Usage: python gallicaMainDriver searchTerm **for shotgun hunt**")
			raise

	else:
		try:
			onePaperHunter = GallicaHunter(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
			onePaperHunter.hunt()
		# Change this eventually
		except:
			print("Usage: python gallicaMainDriver searchTerm recordNumber newspaper")
			raise
main()

"""
cb32757974m_date
cb34431794k_date
cb32858360p_date
cb39294634r_date
cb32895690j_date


"""
