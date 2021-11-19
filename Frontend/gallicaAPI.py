import queue
import random
import re
import threading
import time

from flask import Flask, url_for, render_template, request, redirect
from requests import ReadTimeout

from Backend.GettingAndGraphing.mainSearchSupervisor import MultipleSearchTermHunt
from Frontend.requestForm import SearchForm


class ProgressTrackerThread(threading.Thread):
	def __init__(self, searchTerm, papers, yearRange, strictness, id):
		splitter = re.compile("[\w']+")
		self.searchItems = re.findall(splitter, searchTerm)
		self.paperChoices = papers.split(',')
		self.cleanPaperChoices()
		self.yearRange = re.findall(splitter, yearRange)
		self.strictness = strictness
		self.discoveryProgress = 0
		self.retrievalProgress = 0
		self.currentTerm = ""
		self.threadId = id
		self.imageRef = None
		self.totalResultsForQuery = 0

		super().__init__()

	def run(self):
		requestToRun = MultipleSearchTermHunt(self.searchItems, self.paperChoices, self.yearRange, self.strictness,
											  self, graphType="bar",
											  uniqueGraphs=False, samePage=True)
		try:
			requestToRun.runMultiTermQuery()
		except ReadTimeout:
			gallicaError()

	def cleanPaperChoices(self):
		for i in range(len(self.paperChoices)):
			paper = self.paperChoices[i]
			self.paperChoices[i] = paper.strip()


	def setRetrievalProgress(self, amount):
		self.retrievalProgress = amount

	def setDiscoveryProgress(self, amount):
		self.discoveryProgress = amount

	def getRetrievalProgress(self):
		return self.retrievalProgress

	def getDiscoveryProgress(self):
		return self.discoveryProgress

	def getId(self):
		return self.threadId

	def setImageRef(self, ref):
		self.imageRef = ref

	def getImageRef(self):
		return self.imageRef

	def setDiscoveredResults(self, total):
		self.totalResultsForQuery = total

	def getDiscoveredResults(self):
		return self.totalResultsForQuery




retrievingThreads = {}
exceptionBucket = queue.Queue()
app = Flask(__name__)
app.debug = True
app.secret_key = b'will be made more secret later'


@app.route('/about')
def about():
	return "The about page."


@app.route('/contact')
def contact():
	return "The contact page."


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
	global retrievingThreads
	global exceptionBucket
	form = SearchForm(request.form)
	if request.method == 'POST' and form.validate():

		threadId = str(random.randint(0, 10000)) # What if there is a collision?
		searchTerm = form.searchTerm.data
		threadId = "{keyword}{int}".format(keyword=searchTerm,int=threadId)
		if form.papers.data == "":
			papers = "all"
		else:
			papers = form.papers.data
		yearRange = form.yearRange.data
		strictness = form.strictYearRange.data
		print(searchTerm, papers, yearRange, strictness)
		retrievingThreads[threadId] = ProgressTrackerThread(searchTerm, papers, yearRange, strictness,threadId)
		retrievingThreads[threadId].start()

		return redirect(url_for('loadingResults', threadId=threadId))
	return render_template("mainPage.html", form=form)


@app.route('/results/<threadId>')
def results(threadId):
	global retrievingThreads
	#Clunky. Better way to coordinate between threads?
	imageRef = retrievingThreads[threadId].getImageRef()
	while not imageRef:
		time.sleep(1)
		imageRef = retrievingThreads[threadId].getImageRef()
	return render_template('resultsPage.html',imageRef=imageRef)


@app.route('/loadingResults/<threadId>')
def loadingResults(threadId):
	return render_template('preparingResults.html')


@app.route('/loadingResults/getDiscoveryProgress/<threadId>')
def getDiscoveryProgress(threadId):
	global retrievingThreads
	progress = str(retrievingThreads[threadId].getDiscoveryProgress())
	return progress


@app.route('/loadingResults/getRetrievalProgress/<threadId>')
def getRetrievalProgress(threadId):
	global retrievingThreads
	progress = str(retrievingThreads[threadId].getRetrievalProgress())
	return progress

@app.route('/loadingResults/getDiscoveredResults/<threadId>')
def getTotalDiscovered(threadId):
	global retrievingThreads
	totalDiscovered = str(retrievingThreads[threadId].getDiscoveredResults())
	return totalDiscovered



@app.route('/gallicaError')
def gallicaError():
	return ('Seems like Gallica is messing up.')


if __name__ == "__main__":
	app.run(debug=False)
