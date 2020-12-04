from flask import Flask, url_for, session, render_template, request, redirect
from .requestForm import SearchForm
from Backend.GettingAndGraphing.searchMasterRunner import MultipleSearchTermHunt
import re
import time
import threading
import random

class ProgressTrackerThread(threading.Thread):
	def __init__(self,searchTerm,papers,yearRange,strictness):
		splitter = re.compile("[\w']+")
		self.searchItems = re.findall(splitter, searchTerm)
		self.paperChoices = re.findall(splitter, papers)
		self.yearRange = re.findall(splitter, yearRange)
		self.strictness = strictness
		self.progress = 0
		self.currentTerm = ""
		print(self.searchItems, self.paperChoices, self.yearRange, self.strictness)

		super().__init__()

	def run(self):
		requestToRun = MultipleSearchTermHunt(self.searchItems, self.paperChoices, self.yearRange, self.strictness, graphType="freqPoly",
											  uniqueGraphs=True, samePage=False)
		threadToBeTracked = RetrieverThread(requestToRun)
		threadToBeTracked.start()
		time.sleep(2)
		resultBundles = requestToRun.getAllResultBundlers()
		while threadToBeTracked.is_alive():
			for resultBundle in resultBundles:
				self.currentTerm = resultBundle.getSearchTerm()
				while not resultBundle.getFinishedStatus():
					time.sleep(1)
					self.progress = resultBundle.getPercentProgress()
					print(self.progress)


class RetrieverThread(threading.Thread):
	def __init__(self, requestBundle):
		self.request = requestBundle
		super().__init__()

	def run(self):
		self.request.runMultiTermQuery()


retrievingThreads = {}
app = Flask(__name__)
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
	form = SearchForm(request.form)
	if request.method == 'POST' and form.validate():
		threadId = random.randint(0,10000)
		searchTerm = form.searchTerm.data
		if form.papers.data == "":
			papers = "all"
		else:
			papers = form.papers.data
		yearRange = form.yearRange.data
		if form.strictYearRange.data == "y":
			strictness = True
		else:
			strictness = False
		print(searchTerm, papers, yearRange, strictness)
		retrievingThreads[threadId] = ProgressTrackerThread(searchTerm,papers,yearRange,strictness)
		retrievingThreads[threadId].start()

		return render_template("preparingResults.html")
	return render_template("mainPage.html", form=form)


@app.route('/results')
def results(resultList):
	return "The results page."


@app.route('/loadingResults/<int:threadId>')
def loadingResults(threadId):
	global retrievingThreads
	return str(retrievingThreads[threadId].progress)



if __name__ == "__main__":
	app.run()
