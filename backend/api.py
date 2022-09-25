import os
from flask import Flask
from flask import request
from flask_cors import CORS
import random

from dbops.localPaperSearch import PaperLocalSearch
from dbops.graphSeriesBatch import GraphSeriesBatch
from tasks import spawnRequest
from dbops.topPapersForTicket import TopPapersForTicket
from dbops.recordDataForUser import RecordDataForUser


app = Flask(__name__)
CORS(app)
userData = RecordDataForUser()
requestID = random.randint(0, 10000)


@app.route('/')
def index():
    return 'ok'


@app.route('/api/init', methods=['POST'])
def init():
    global requestID
    requestID += 1
    tickets = request.get_json()["tickets"]
    task = spawnRequest.delay(tickets, requestID)
    return {"taskid": task.id, "requestid": requestID}


@app.route('/poll/progress/<taskID>')
def getProgress(taskID):
    task = spawnRequest.AsyncResult(taskID)
    state = task.state
    if state == 'PENDING':
        response = {
            'state': state,
            'progress': 0
        }
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
        elif result and result['status'] == 'No records found!':
            response = {
                'state': "NO_RECORDS"
            }
        else:
            response = {'state': "SUCCESS"}
    return response


@app.route('/api/revokeTask/<taskID>/<reqID>')
def revokeTask(taskID, reqID):
    task = spawnRequest.AsyncResult(taskID)
    task.revoke(terminate=True)
    userData.clearUserRecordsAfterCancel(reqID)
    return {'state': "REVOKED"}


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
        'dateRange': request.args["dateRange"],
        'requestID': request.args["requestID"]
    }
    series = GraphSeriesBatch(settings)
    items = {'series': series.getSeriesBatch()}
    return items


@app.route('/api/topPapers')
def getTopPapersFromID():
    topPapers = TopPapersForTicket(
        ticketID=request.args["ticketID"],
        requestID=request.args["requestID"],
        continuous=request.args["continuous"],
        dateRange=request.args["dateRange"]
    )
    items = {"topPapers": topPapers.getTopPapers()}
    return items


@app.route('/api/getcsv')
def getCSV():
    tickets = request.args["tickets"]
    requestID = request.args["requestID"]
    csvData = userData.getCSVData(tickets, requestID)
    return {"csvData": csvData}


@app.route('/api/getDisplayRecords')
def getDisplayRecords():
    tableArgs = dict(request.args)
    del tableArgs['uniqueforcache']
    tableArgs['tickets'] = tuple(tableArgs['tickets'].split(','))
    displayRecords, count = userData.getRecordsForDisplay(tableArgs)
    return {"displayRecords": displayRecords,
            "count": count}


@app.route('/api/ocrtext/<arkCode>/<term>')
def getOCRtext(arkCode, term):
    numResults, text = userData.getOCRTextForRecord(
        arkCode,
        term
    )
    return {"numResults": numResults, "text": text}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
