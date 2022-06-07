import queue
from flask import Flask
from flask import request
from flask_cors import CORS

from api.gallica.newspaper import Newspaper
from api.gallica.ticketGraphData import TicketGraphData
from api.tasks import spawnRequestThread

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
    response = {
        'state': task.state,
        'progress': task.info.get('progress'),
        'currentID': task.info.get('currentID')
    }
    return response


@app.route('/paperchartjson')
def paperChart():
    with open('./static/paperJSON.json', 'r') as outFile:
        paperChartJSON = outFile.read()
    return paperChartJSON


@app.route('/papers/<query>')
def papers(query):
    newspapers = Newspaper()
    availablePapers = newspapers.getPapersSimilarToKeyword(query)
    return availablePapers


@app.route('/graphData')
def getGraphData():
    graphData = TicketGraphData(
        request.args["key"],
        averagewindow=request.args["averageWindow"],
        groupby=request.args["timeBin"])
    graphJSON = graphData.getGraphJSON()
    items = {'graphJSON': graphJSON}
    return items


if __name__ == "__main__":
    app.run(debug=True)
