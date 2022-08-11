import os
import queue
from flask import Flask
from flask import request
from flask_cors import CORS

from gallica.newspaper import Newspaper
from gallica.ticketGraphSeriesBatch import TicketGraphSeriesBatch
from tasks import spawnRequestThread
from gallica.topPapers import TopPapers

retrievingThreads = {}
exceptionBucket = queue.Queue()
app = Flask(__name__)
CORS(app)


@app.route('/init', methods=['POST'])
def init():
    tickets = request.get_json()["tickets"]
    task = spawnRequestThread.delay(tickets)
    return {"taskid": task.id}


@app.route('/progress/<taskID>')
def getProgress(taskID):
    task = spawnRequestThread.AsyncResult(taskID)
    if task.info:
        response = {
            'state': task.state,
            'progress': task.info.get('progress')
        }
    else:
        response = {
            'state': task.state,
            'progress': None
        }
    return response


@app.route('/paperchartjson')
def paperChart():
    with open(os.path.join(os.path.dirname(__file__), 'static/paperJSON.json'), 'r') as outFile:
        paperChartJSON = outFile.read()
    return paperChartJSON


@app.route('/papers/<query>')
def papers(query):
    newspapers = Newspaper()
    availablePapers = newspapers.getPapersSimilarToKeyword(query)
    return availablePapers


@app.route('/graphData')
def getGraphData():
    settings = {
        'ticketIDs': request.args["keys"],
        'averageWindow': request.args["averageWindow"],
        'groupBy': request.args["timeBin"],
        'continuous': request.args["continuous"],
        'dateRange': request.args["dateRange"]
    }
    series = TicketGraphSeriesBatch(settings)
    items = {'series': series.getSeriesBatch()}
    return items


@app.route('/topPapers')
def getTopPapersFromID():
    topPapers = TopPapers(
        request.args["id"],
        continuous=request.args["continuous"],
        dateRange=request.args["dateRange"]
    )
    items = {"topPapers": topPapers.getTopPapers()}
    return items


if __name__ == "__main__":
    app.run(debug=True)
