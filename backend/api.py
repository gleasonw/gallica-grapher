import os
from flask import Flask
from flask import request
from flask_cors import CORS

from dbops.localPaperSearch import PaperLocalSearch
from dbops.graphSeriesBatch import GraphSeriesBatch
from tasks import spawnRequest
from dbops.topPapersForTicket import TopPapersForTicket
from dbops.reactCSVdata import ReactCSVdata


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
    state = task.state
    if state == 'PENDING':
        response = {'state': state}
    elif state == 'PROGRESS':
        response = {
            'state': state,
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


@app.route('/api/papers/<keyword>')
def papers(keyword):
    search = PaperLocalSearch()
    similarPapers = search.selectPapersSimilarToKeyword(keyword)
    return similarPapers


@app.route('/api/numPapersOverRange/<startYear>/<endYear>')
def numPapersOverRange(startYear, endYear):
    search = PaperLocalSearch()
    numPapers = search.getNumPapersInRange(
        startYear,
        endYear
    )
    return {'numPapersOverRange': numPapers}


@app.route('/api/continuousPapers')
def getContinuousPapersOverRange():
    limit = request.args.get('limit')
    startYear = request.args.get('startYear')
    endYear = request.args.get('endYear')
    search = PaperLocalSearch()
    selectPapers = search.selectPapersContinuousOverRange(
        startYear,
        endYear,
        limit
    )
    return selectPapers


@app.route('/api/graphData')
def getGraphData():
    settings = {
        'ticketIDs': request.args["keys"],
        'averageWindow': request.args["averageWindow"],
        'groupBy': request.args["timeBin"],
        'continuous': request.args["continuous"],
        'dateRange': request.args["dateRange"]
    }
    series = GraphSeriesBatch(settings)
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


@app.route('/getIssueLinks')
def getIssueLinks():
    tickets = request.args["tickets"]
    startDate = request.args["startDate"]
    endDate = request.args["endDate"]
    paperLinks = ReactCSVdata().getIssueLinks(tickets, startDate, endDate)
    return {"paperLinks": paperLinks}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
