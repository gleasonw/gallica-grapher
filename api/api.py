import os
import queue

import psycopg2
from flask import Flask, jsonify

from Backend.GettingAndGraphing.UIPaperFetcher import UIPaperFetcher
from tasks import getAsyncRequest

retrievingThreads = {}
exceptionBucket = queue.Queue()
app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
basedir = os.path.abspath(os.path.dirname(__file__))
pathToPaperJSON = os.path.join(basedir, 'static/paperJSON.json')


@app.route('/about')
def about():
    return "The about page."


@app.route('/contact')
def contact():
    return "The contact page."


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return "hello"


@app.route('/loadingResults/progress/<taskID>')
def getProgress(taskID):
    task = getAsyncRequest.AsyncResult(taskID)
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


@app.route('/paperchartjson')
def paperChart():
    with open(pathToPaperJSON, 'r') as outFile:
        paperChartJSON = outFile.read()
    return paperChartJSON


# TODO: Query database based on keywords
@app.route('/papers/<query>')
def papers(query):
    conn = None
    # TODO: Make sure the database pattern corresponds to norms
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        getter = UIPaperFetcher(conn)
        availablePapers = getter.getPapersLikeString(query)
    finally:
        if conn is not None:
            conn.close()
    return availablePapers


@app.route('/results/<taskID>/graphData')
def getGraphData(taskID):
    task = getAsyncRequest.AsyncResult(taskID)
    queryResults = task.get()
    graphJSON = queryResults.get('graphJSON')
    infoStats = queryResults.get('infoStats')
    items = {'graphJSON': graphJSON,
             'paperAndInfoStats': infoStats,
             }
    return items


@app.route('/loadingResults/getDiscoveredResults/<taskID>')
def getTotalDiscovered(taskID):
    task = getAsyncRequest.AsyncResult(taskID)
    numberDiscovered = task.info.get('totalDiscovered')
    numberDiscovered = "{:,}".format(int(numberDiscovered))
    return jsonify({'numberDiscovered': numberDiscovered})


@app.route('/loadingResults/getNumberRetrievedResults/<taskID>')
def getTotalRetrieved(taskID):
    task = getAsyncRequest.AsyncResult(taskID)
    numberRetrieved = task.info.get('totalRetrieved')
    return jsonify({'numberRetrieved': numberRetrieved})


@app.route('/gallicaError')
def gallicaError():
    return ('Seems like Gallica is messing up.')


if __name__ == "__main__":
    app.run(debug=True)
