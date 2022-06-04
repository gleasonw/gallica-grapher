import os
import queue
import psycopg2
from flask import Flask, jsonify

from gallica.newspaper import Newspaper
from tasks import getAsyncRequest
from ticketGraphData import TicketGraphData

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
    newspapers = Newspaper()
    availablePapers = newspapers.getPapersSimilarToKeyword(query)
    return availablePapers


@app.route('/graphData/<requestid>/<window>/<timegroup>/')
def getGraphData(requestid, window, timegroup):
    graphData = TicketGraphData(
        requestid,
        averagewindow=window,
        groupby=timegroup)
    graphJSON = graphData.getGraphJSON()
    items = {'graphJSON': graphJSON}
    return items


if __name__ == "__main__":
    app.run(debug=True)
