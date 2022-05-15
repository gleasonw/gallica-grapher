from api.requestThread import RequestThread
from celery import Celery
import time

celery = Celery('tasks', broker='redis://localhost:6379/0')
celery.conf.result_backend = 'redis://localhost:6379/0'

@celery.task(bind=True)
def getAsyncRequest(self, papers, terms, yearRange, yearStrict, splitPapers, splitTerms, taskID):
	gallicaRequest = RequestThread(terms, papers, yearRange, taskID, termTrendLines=splitTerms,
								   eliminateEdgePapers=yearStrict, paperTrendLines=splitPapers)
	gallicaRequest.start()
	for term in terms:
		while gallicaRequest.getDiscoveryProgress() < 100:
			self.update_state(state="DPROGRESS", meta={'percent': gallicaRequest.getDiscoveryProgress(),
													   'term': term,
													   'numTerms': len(terms),
													   'status': "Discovering total results...",
													   'totalDiscovered': 0,
													   'totalRetrieved': 0})
		self.update_state(state="RPROGRESS", meta={'percent': gallicaRequest.getRetrievalProgress(),
												   'term': term,
												   'numTerms': len(terms),
												   'status': "Retrieving results...",
												   'totalDiscovered': gallicaRequest.getNumberDiscoveredResults(),
												   'totalRetrieved': 0})
		while gallicaRequest.getRetrievalProgress() < 100:
			self.update_state(state="RPROGRESS", meta={'percent': gallicaRequest.getRetrievalProgress(),
													   'status': "Retrieving results...",
													   'term': term,
													   'numTerms': len(terms),
													   'totalDiscovered': gallicaRequest.getNumberDiscoveredResults(),
													   'totalRetrieved': 0})
	while not gallicaRequest.getGraphJSON():
		time.sleep(.5)
	self.update_state(state="GRAPHING", meta={'percent': 100,
											  'status': "Graphing results...",
											  'totalDiscovered': gallicaRequest.getNumberDiscoveredResults(),
											  'totalRetrieved': gallicaRequest.getNumberRetrievedResults()})
	self.update_state(state="SUCCESS", meta={'status': "All done.",
											 'searchTerms': gallicaRequest.getSearchItems(),
											 'dateRange': gallicaRequest.getDateRangeString(),
											 'topPapers': gallicaRequest.getTopPapers(),
											 'graphJSON': gallicaRequest.getGraphJSON()})
	return {'percent': 100, 'status': 'Complete!', 'result': 42}