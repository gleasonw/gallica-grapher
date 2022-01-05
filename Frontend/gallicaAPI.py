import queue
import time
import os
from flask import Flask, url_for, render_template, request, redirect, g
from Backend.GettingAndGraphing.paperGetter import PaperGetter
from Frontend.requestForm import SearchForm
from requestThread import RequestThread

retrievingThreads = {}
exceptionBucket = queue.Queue()
app = Flask(__name__)
app.secret_key = os.urandom(12).hex()


@app.route('/about')
def about():
	return "The about page."


@app.route('/contact')
def contact():
	return "The contacage."


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
	global retrievingThreads
	global exceptionBucket
	form = SearchForm(request.form)
	if request.method == 'POST' and form.validate():
		searchTerm = form.searchTerm.data
		yearRange = form.yearRange.data
		strictness = form.strictYearRange.data
		papers = request.form['chosenPapers']
		g.searchTerm = searchTerm
		g.yearRange = yearRange
		g.strictness = strictness
		g.papers = parsePapers(papers)
		print(g.papers)
		getAsyncRequest()
		return redirect(url_for('loadingResults'))
	return render_template("mainPage.html", form=form)

def parsePapers(rawPapers):
	listPapers = rawPapers.split("%8395%")
	return listPapers



def getAsyncRequest():
	gallicaRequest = RequestThread(g.searchTerm, g.papers, g.yearRange, g.strictness)
	gallicaRequest.start()
	g.requestThread = gallicaRequest
	return


@app.route('/papers')
def papers():
	getter = PaperGetter()
	availablePapers = getter.getPapers()
	return availablePapers


@app.route('/results')
def results():
	# Clunky. Is there a better way to coordinate waiting for the graph to finish?
	imageRef = g.requestThread.getImageRef()

	while not imageRef:
		time.sleep(1)
		imageRef = g.requestThread.getImageRef()

	# This will need to be changed for multiple terms, multiple dictionaries.
	searchTerms = g.requestThread.getSearchItems()
	dateRange = g.requestThread.getDateRange()
	paperDictionarys = g.requestThread.getTopPapers()
	singleDictionaryForSingleTerm = paperDictionarys[0]
	return render_template('resultsPage.html', imageRef=imageRef, topPapers=singleDictionaryForSingleTerm,
						   dateRange=dateRange, term=searchTerms)


@app.route('/loadingResults')
def loadingResults():
	return render_template('preparingResults.html')


@app.route('/loadingResults/getDiscoveryProgress')
def getDiscoveryProgress():
	global retrievingThreads
	progress = str(g.requestThread.getDiscoveryProgress())
	return progress


@app.route('/loadingResults/getRetrievalProgress')
def getRetrievalProgress():
	global retrievingThreads
	progress = str(g.requestThread.getRetrievalProgress())
	return progress


@app.route('/loadingResults/getDiscoveredResults')
def getTotalDiscovered():
	global retrievingThreads
	totalDiscovered = g.requestThread.getDiscoveredResults()
	return totalDiscovered


@app.route('/loadingResults/getNumberRetrievedResults')
def getTotalRetrieved():
	global retrievingThreads
	totalRetrieved = g.requestThread.getNumberRetrievedResults()
	return totalRetrieved


@app.route('/gallicaError')
def gallicaError():
	return ('Seems like Gallica is messing up.')


if __name__ == "__main__":
	app.run(debug=True)
