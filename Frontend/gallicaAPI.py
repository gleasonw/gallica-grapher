import queue
import redis
import time
import os
from flask import Flask, url_for, render_template, request, redirect, session, jsonify
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
		papers = parsePapers(papers)
		term = form.searchTerm.data
		yearRange = form.yearRange.data
		yearStrict = form.strictYearRange.data
		task = getAsyncRequest.apply_async(args=[papers, term, yearRange, yearStrict])
		return jsonify({}), 202, {'Location': url_for('loadingResults', task_id=task.id)}
	return render_template("mainPage.html", form=form)


@celery.task(bind=True)
def getAsyncRequest(self, papers, term, yearRange, yearStrict):
	gallicaRequest = RequestThread(term, papers, yearRange, yearStrict)
	gallicaRequest.start()
	while gallicaRequest.getDiscoveryProgress() < 100:
		self.update_state(state="DPROGRESS", meta={'percent': gallicaRequest.getDiscoveryProgress(),
												   'status': "Discovering total results...",
												   'totalDiscovered': 0,
		 										   'totalRetrieved': 0})
	self.update_state(state="RPROGRESS", meta={'percent': gallicaRequest.getRetrievalProgress(),
											   'status': "Retrieving results...",
											   'totalDiscovered': gallicaRequest.getDiscoveredResults(),
											   'totalRetrieved': 0})
	while gallicaRequest.getRetrievalProgress() < 100:
		self.update_state(state="RPROGRESS", meta={'percent': gallicaRequest.getRetrievalProgress(),
												   'status': "Retrieving results...",
												   'totalDiscovered': 0,
												   'totalRetrieved': 0})
	self.update_state(state="SUCCESS", meta={'percent': 100,
											 'status': "Completed...",
											 'totalDiscovered': gallicaRequest.getDiscoveredResults(),
											 'totalRetrieved': gallicaRequest.getNumberRetrievedResults()})
	return {'percent': 100, 'status': 'Complete!', 'result': 42}


@app.route('/papers')
def papers():
	getter = PaperGetter()
	availablePapers = getter.getPapers()
	return availablePapers


@app.route('/results')
def results():
	request = session['fetchThread']
	# Clunky. Is there a better way to coordinate waiting for the graph to finish?
	imageRef = request.getImageRef()

	while not imageRef:
		time.sleep(1)
		imageRef = session['fetchThread'].getImageRef()

	# This will need to be changed for multiple terms, multiple dictionaries.
	searchTerms = request.getSearchItems()
	dateRange = request.getDateRange()
	paperDictionarys = request.getTopPapers()
	singleDictionaryForSingleTerm = paperDictionarys[0]
	return render_template('resultsPage.html', imageRef=imageRef, topPapers=singleDictionaryForSingleTerm,
						   dateRange=dateRange, term=searchTerms)


@app.route('/loadingResults/<task_id>')
def loadingResults(task_id):
	return render_template('preparingResults.html')


@app.route('/loadingResults/progress/<task_id>')
def getDiscoveryRetrievalProgress(task_id):
	task = getAsyncRequest.AsyncResult(task_id)
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
	else:
		response = {
			'state': task.state,
			'discoveryPercent': 0,
			'retrievalPercent': 0,
			'status': str(task.info)
		}
	return jsonify(response)


@app.route('/loadingResults/getDiscoveredResults/<task_id>')
def getTotalDiscovered(task_id):
	task = getAsyncRequest.AsyncResult(task_id)
	numberDiscovered = task.info.get('totalDiscovered')
	return jsonify({'numberDiscovered' : numberDiscovered})


@app.route('/loadingResults/getNumberRetrievedResults/<task_id>')
def getTotalRetrieved(task_id):
	task = getAsyncRequest.AsyncResult(task_id)
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
