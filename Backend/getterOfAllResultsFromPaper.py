from Backend.gallica50BatchGetter import GallicaHunter
from math import ceil
from requests_toolbelt import sessions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class OverseerOfNewspaperHunt:

	def __init__(self, query, numberResults):
		self.numPurgedResults = 0
		self.currentProcessedResults = 0
		self.startRecordForGallicaQuery = 1
		self.query = query
		self.numberResults = numberResults
		self.allResults = []
		self.queryList = []
		self.gallicaHttpSession = None
		self.buildHttpSession()

	def buildHttpSession(self):
		self.gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
		assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
		self.gallicaHttpSession.hooks["response"] = assert_status_hook
		adapter = TimeoutAndRetryHTTPAdapter(timeout=2.5)
		self.gallicaHttpSession.mount("https://", adapter)
		self.gallicaHttpSession.mount("http://", adapter)

	def scourPaper(self):
		pass

	def getResultList(self):
		return self.allResults

	def sendQuery(self, startRecord, numRecords):
		hunter = GallicaHunter(self.query, startRecord, numRecords, self.gallicaHttpSession)
		hunter.hunt()
		return hunter

	def getNumValidResults(self):
		return len(self.allResults)

	def getNumProcessedResults(self):
		return len(self.allResults) + self.numPurgedResults


class LimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults, maxResults):
		super().__init__(query, numberResults)
		self.maxResults = maxResults

	# Something is wrong here...
	def scourPaper(self):

		while self.maxResults > self.currentProcessedResults:
			amountRemaining = self.maxResults - self.currentProcessedResults
			if amountRemaining >= 50:
				numRecords = 50
			else:
				numRecords = amountRemaining
			batchHunter = OverseerOfNewspaperHunt.sendQuery(self.query, self.startRecordForGallicaQuery, numRecords)


class UnlimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults):
		super().__init__(query, numberResults)

	def scourPaper(self):
		numberQueriesToSend = ceil(self.numberResults / 50)
		for i in range(numberQueriesToSend):
			result = self.createGallicaHunters(i)
			queryResults = result[0]
			numPurged = result[1]
			self.numPurgedResults = self.numPurgedResults + numPurged
			self.allResults = self.allResults + queryResults

	# Based on some not-so-rigorous testing threading the requests themselves, rather than the papers, is slower.

	# numCpus = cpu_count()
	# processes = min(numCpus, numberQueriesToSend)
	# with Pool(processes) as pool:
	# 	chunkSize = ceil(numberQueriesToSend / processes)
	# 	for result in pool.imap(self.createGallicaHunters, range(numberQueriesToSend), chunksize=chunkSize):
	# 		queryResults = result[0]
	# 		numPurged = result[1]
	# 		self.numPurgedResults = self.numPurgedResults + numPurged
	# 		self.allResults = self.allResults + queryResults

	def createGallicaHunters(self, iterationNumber):
		startRecord = iterationNumber * 50
		startRecord = startRecord + 1
		batchHunter = self.sendQuery(startRecord, 50)
		return [batchHunter.getResultList(), batchHunter.getNumberPurgedResults()]

DEFAULT_TIMEOUT = 5  # seconds


class TimeoutAndRetryHTTPAdapter(HTTPAdapter):
	def __init__(self, *args, **kwargs):
		retryStrategy = Retry(
			total=3,
			status_forcelist=[429, 500, 502, 503, 504],
			method_whitelist=["HEAD", "GET", "OPTIONS", "PUT", "DELETE"],
			backoff_factor=1
		)
		self.timeout = DEFAULT_TIMEOUT
		if "timeout" in kwargs:
			self.timeout = kwargs["timeout"]
			del kwargs["timeout"]
		super().__init__(*args, **kwargs, max_retries=retryStrategy)

	def send(self, request, **kwargs):
		timeout = kwargs.get("timeout")
		if timeout is None:
			kwargs["timeout"] = self.timeout
		return super().send(request, **kwargs)
