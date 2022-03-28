import queue
import uuid
import time
import os
from flask import Flask, url_for, render_template, request, session, jsonify
from celery import Celery
from Backend.GettingAndGraphing.paperGetter import PaperGetter
from Frontend.requestForm import SearchForm
from Frontend.requestThread import RequestThread

retrievingThreads = {}
exceptionBucket = queue.Queue()
app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery('Frontend.gallicaAPI', broker=app.config['CELERY_BROKER_URL'])
celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
celery.autodiscover_tasks()

@app.route('/about')
def about():
	return "The about page."


@app.route('/contact')
def contact():
	return "The contact page."


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
	form = SearchForm(request.form)
	if request.method == 'POST' and form.validate():
		papers = request.form['chosenPapers']
		if request.form['strictness'] == "false":
			yearStrict = False
		else:
			yearStrict = True
		papers = parsePapers(papers)
		term = form.searchTerm.data
		yearRange = form.yearRange.data
		taskID = str(uuid.uuid4())
		getAsyncRequest.apply_async(args=[papers, term, yearRange, yearStrict, taskID], task_id=taskID)
		return jsonify({}), 202, {'Location': url_for('loadingResults', taskId=taskID)}
	return render_template("mainPage.html", form=form)


@celery.task(bind=True)
def getAsyncRequest(self, papers, term, yearRange, yearStrict, taskID):
	gallicaRequest = RequestThread(term, papers, yearRange, yearStrict, taskID)
	gallicaRequest.start()
	while gallicaRequest.getDiscoveryProgress() < 100:
		self.update_state(state="DPROGRESS", meta={'percent': gallicaRequest.getDiscoveryProgress(),
												   'status': "Discovering total results...",
												   'totalDiscovered': 0,
		 										   'totalRetrieved': 0})
	self.update_state(state="RPROGRESS", meta={'percent': gallicaRequest.getRetrievalProgress(),
											   'status': "Retrieving results...",
											   'totalDiscovered': gallicaRequest.getNumberDiscoveredResults(),
											   'totalRetrieved': 0})
	while gallicaRequest.getRetrievalProgress() < 100:
		self.update_state(state="RPROGRESS", meta={'percent': gallicaRequest.getRetrievalProgress(),
												   'status': "Retrieving results...",
												   'totalDiscovered': gallicaRequest.getNumberDiscoveredResults(),
												   'totalRetrieved': 0})
	self.update_state(state="GRAPHING", meta={'percent': 100,
												   'status': "Graphing results...",
												   'totalDiscovered': gallicaRequest.getNumberDiscoveredResults(),
												   'totalRetrieved': gallicaRequest.getNumberRetrievedResults()})
	while not gallicaRequest.getGraphingStatus():
		time.sleep(.5)
	self.update_state(state="SUCCESS", meta={'status': "All done.",
											 'searchTerms': gallicaRequest.getSearchItems(),
											 'dateRange': gallicaRequest.getDateRange(),
											 'topPapers': gallicaRequest.getTopPapers()})
	return {'percent': 100, 'status': 'Complete!', 'result': 42}


@app.route('/loadingResults/progress/<taskId>')
def getProgress(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	if task.state == "PENDING":
		response = {
			'state': task.state,
			'discoveryPercent': 0,
			'retrievalPercent': 0,
			'status': 'Pending...'
		}
	elif task.state == "DPROGRESS":
		response = {
			'state': task.state,
			'discoveryPercent': task.info.get('percent'),
			'retrievalPercent': 0,
		}
	elif task.state == "RPROGRESS":
		response = {
			'state': task.state,
			'discoveryPercent': 100,
			'retrievalPercent': task.info.get('percent'),
		}
	elif task.state == "GRAPHING" or task.state == "SUCCESS":
		response = {
			'state': task.state,
			'discoveryPercent': 100,
			'retrievalPercent': 100,
			'status': str(task.info)
		}
	else:
		response = {
			'state': task.state,
			'discoveryPercent': 0,
			'retrievalPercent': 0,
			'status': str(task.info)
		}
	return jsonify(response)


@app.route('/papers')
def papers():
	getter = PaperGetter()
	availablePapers = getter.getPapers()
	return availablePapers


@app.route('/results/<taskId>')
def results(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	results = task.get()
	searchTerms = results.get('searchTerms')
	dateRange = results.get('dateRange')
	#TODO: investigate why toppapers only sending one
	topPapers = results.get('topPapers')
	return render_template('resultsPage.html', topPapers=topPapers,
						   dateRange=dateRange, term=searchTerms, requestID=taskId)


@app.route('/loadingResults/<taskId>')
def loadingResults(taskId):
	return render_template('preparingResults.html')

@app.route('/loadingResults/getDiscoveredResults/<taskId>')
def getTotalDiscovered(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	numberDiscovered = task.info.get('totalDiscovered')
	numberDiscovered = "{:,}".format(int(numberDiscovered))
	return jsonify({'numberDiscovered' : numberDiscovered})


@app.route('/loadingResults/getNumberRetrievedResults/<taskId>')
def getTotalRetrieved(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	numberRetrieved = task.info.get('totalRetrieved')
	return jsonify({'numberRetrieved' : numberRetrieved})


@app.route('/gallicaError')
def gallicaError():
	return ('Seems like Gallica is messing up.')


def parsePapers(rawPapers):
	listPapers = rawPapers.split("%8395%")
	listPapers.pop(-1)
	return listPapers


if __name__ == "__main__":
	app.run(debug=False)
