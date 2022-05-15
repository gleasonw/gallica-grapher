import queue, ast, uuid, os
from flask import Flask, url_for, render_template, request, jsonify
from Backend.GettingAndGraphing.UIPaperFetcher import UIPaperFetcher
from Frontend.requestForm import SearchForm
from Frontend.tasks import getAsyncRequest

retrievingThreads = {}
exceptionBucket = queue.Queue()
app = Flask(__name__)
app.secret_key = os.urandom(12).hex()


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
		if request.form['strictness'] == "false":
			yearStrict = False
		else:
			yearStrict = True
		if request.form['splitpapers'] == "false":
			splitPapers = False
		else:
			splitPapers = True
		if request.form['splitterms'] == "false":
			splitTerms = False
		else:
			splitTerms = True
		try:
			papers = ast.literal_eval(request.form['papers'])
			terms = ast.literal_eval(request.form['searchTerm'])
		except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
			return
		yearRange = form.yearRange.data
		taskID = str(uuid.uuid4())
		getAsyncRequest.apply_async(args=[papers, terms, yearRange, yearStrict, splitPapers, splitTerms, taskID],
									task_id=taskID)
		return jsonify({}), 202, {'Location': url_for('loadingResults', taskId=taskID)}
	return render_template("mainPage.html", form=form)


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
			'term': task.info.get('term'),
			'discoveryPercent': task.info.get('percent'),
			'retrievalPercent': 0,
		}
	elif task.state == "RPROGRESS":
		response = {
			'state': task.state,
			'term': task.info.get('term'),
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
	getter = UIPaperFetcher()
	availablePapers = getter.getPapers()
	return availablePapers


@app.route('/results/<taskId>')
def results(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	results = task.get()
	topPapers = results.get('topPapers')
	return render_template('resultsPage.html', topPapers=topPapers)


@app.route('/results/<taskId>/graphData')
def getGraphData(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	queryResults = task.get()
	searchTerms = queryResults.get('searchTerms')
	dateRange = queryResults.get('dateRange')
	graphJSON = queryResults.get('graphJSON')
	graphVals = {'terms': searchTerms, 'dateRange': dateRange, 'data': graphJSON}
	return graphVals


@app.route('/loadingResults/<taskId>')
def loadingResults(taskId):
	return render_template('preparingResults.html')


@app.route('/loadingResults/getNumberTerms/<taskId>')
def getNumberTerms(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	taskData = task.get()
	numberOfTerms = taskData.get('numTerms')
	return {'numberOfTerms' : numberOfTerms}


@app.route('/loadingResults/getDiscoveredResults/<taskId>')
def getTotalDiscovered(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	numberDiscovered = task.info.get('totalDiscovered')
	numberDiscovered = "{:,}".format(int(numberDiscovered))
	return jsonify({'numberDiscovered': numberDiscovered})


@app.route('/loadingResults/getNumberRetrievedResults/<taskId>')
def getTotalRetrieved(taskId):
	task = getAsyncRequest.AsyncResult(taskId)
	numberRetrieved = task.info.get('totalRetrieved')
	return jsonify({'numberRetrieved': numberRetrieved})


@app.route('/gallicaError')
def gallicaError():
	return ('Seems like Gallica is messing up.')


if __name__ == "__main__":
	app.run(debug=True)
