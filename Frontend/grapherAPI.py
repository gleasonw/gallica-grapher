from flask import Flask, url_for
from flask import render_template, request, redirect
from requestForm import SearchForm

app = Flask(__name__)

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
		searchTerm = form.searchTerm
		papers = form.papers
		yearRange = form.yearRange
		strictness = form.strictYearRange
		print(searchTerm, papers, yearRange, strictness)
	return render_template("mainPage.html", form=form)

@app.route('/results')
def results():
	return "The results page."

@app.route('/loadingResults')
def loadingResults():
	return "The loading page."

