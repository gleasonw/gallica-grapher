from gallicaHunter import GallicaHunter
import sys

def main():
	hunter = GallicaHunter()
	if len(sys.argv) == 2:
		try:
			hunter.huntBigSix(sys.argv[1])
		# Change this eventually
		except:
			print("Usage: python gallicaMainDriver searchTerm **for shotgun hunt**")
			raise
		
	else:
		try:
			hunter.hunt(sys.argv[1], int(sys.argv[2]), sys.argv[3])
		# Change this eventually
		except:
			print("Usage: python gallicaMainDriver searchTerm recordNumber newspaperKey")
			raise
main()

"""
cb32757974m_date
cb34431794k_date
cb32858360p_date
cb39294634r_date
cb32895690j_date


"""