import os
import queue
import psycopg2
from flask import Flask, jsonify

from UINewspaper import UINewspaper
from tasks import getAsyncRequest

retrievingThreads = {}
exceptionBucket = queue.Queue()
app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
basedir = os.path.abspath(os.path.dirname(__file__))
pathToPaperJSON = os.path.join(basedir, 'static/paperJSON.json')


@app.route('/loadingResults/progress/<taskID>')
def getProgress(taskID):
    task = getAsyncRequest.AsyncResult(taskID)
    if task.state == "FAILURE":
        response = {
            'state': task.state,
            'percent': 0,
            'status': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'percent': task.info.get('percent'),
        }
    return jsonify(response)


@app.route('/paperchartjson')
def paperChart():
    with open(pathToPaperJSON, 'r') as outFile:
        paperChartJSON = outFile.read()
    return paperChartJSON


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
        getter = UINewspaper(conn)
        availablePapers = getter.getPapersSimilarToString(query)
    finally:
        if conn is not None:
            conn.close()
    return availablePapers


@app.route('/graphData/<taskID>')
def getGraphData(taskID):
    task = getAsyncRequest.AsyncResult(taskID)
    queryResults = task.get()
    graphJSON = queryResults.get('graphJSON')
    infoStats = queryResults.get('infoStats')
    items = {'graphJSON': graphJSON,
             'paperAndInfoStats': infoStats,
             }
    return items


if __name__ == "__main__":
    app.run(debug=True)
