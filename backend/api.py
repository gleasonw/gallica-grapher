import os
from flask import Flask
from flask import request
from flask_cors import CORS

from scripts.newspaper import Newspaper
from scripts.ticketGraphSeriesBatch import TicketGraphSeriesBatch
from tasks import spawnRequest
from scripts.topPapersForTicket import TopPapersForTicket
from scripts.reactCSVdata import ReactCSVdata


app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return 'ok'


@app.route('/api/init', methods=['POST'])
def init():
    tickets = request.get_json()["tickets"]
    task = spawnRequest.delay(tickets)
    return {"taskid": task.id}


@app.route('/api/progress/<taskID>')
def getProgress(taskID):
    task = spawnRequest.AsyncResult(taskID)
    if task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'progress': task.info.get('progress')
        }
    else:
        result = task.result
        if result and result['status'] == 'Too many records!':
            response = {
                'state': "TOO_MANY_RECORDS",
                'numRecords': result['numRecords']
            }
        else:
            response = {'state': "SUCCESS"}
    return response


@app.route('/api/paperchartjson')
def paperChart():
    with open(os.path.join(os.path.dirname(__file__), 'static/paperJSON.json'), 'r') as outFile:
        paperChartJSON = outFile.read()
    return paperChartJSON


@app.route('/api/papers/<query>')
def papers(query):
    newspapers = Newspaper()
    availablePapers = newspapers.getPapersSimilarToKeyword(query)
    return availablePapers


@app.route('/api/graphData')
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


@app.route('/api/topPapers')
def getTopPapersFromID():
    topPapers = TopPapersForTicket(
        request.args["id"],
        continuous=request.args["continuous"],
        dateRange=request.args["dateRange"]
    )
    items = {"topPapers": topPapers.getTopPapers()}
    return items


@app.route('/api/getcsv')
def getCSV():
    tickets = request.args["tickets"]
    csvData = ReactCSVdata().getCSVData(tickets)
    return {"csvData": csvData}



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
