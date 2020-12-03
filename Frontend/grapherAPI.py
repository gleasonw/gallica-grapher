from flask import Flask, url_for, session, render_template, request, redirect
from requestForm import SearchForm
from Backend.GettingAndGraphing.searchMasterRunner import MultipleSearchTermHunt
import re

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
	form = SearchForm(request.form)
	if request.method == 'POST' and form.validate():
		session['searchTerm'] = form.searchTerm.data
		session['papers'] = form.papers.data
		session['yearRange'] = form.yearRange.data
		session['strictness'] = form.strictYearRange
		return (redirect(url_for('loadingResults')))
	return render_template("mainPage.html", form=form)


@app.route('/results')
def results():
	return "The results page."


@app.route('/loadingResults')
def loadingResults():
	splitter = re.compile("[\w']+")
	searchItems = re.findall(splitter, session['searchTerm'])
	paperChoices = re.findall(splitter, session['papers'])
	yearRange = re.findall(splitter, session['yearRange'])
	strictness = session['strictness']
	requestToRun = MultipleSearchTermHunt(searchItems, paperChoices, yearRange, strictness, graphType="freqPoly",
										  uniqueGraphs=True, samePage=False)
	requestToRun.runMultiTermQuery()
	#TO DO: PROGRESS BAR
	return "The loading page."
