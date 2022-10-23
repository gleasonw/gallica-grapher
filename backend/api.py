import os
from flask import Flask
from flask import request
from flask_cors import CORS
import random
import json

from dbops.localPaperSearch import PaperLocalSearch
from dbops.graphSeriesBatch import GraphSeriesBatch
from tasks import spawnRequest
from dbops.recordDataForUser import RecordDataForUser

app = Flask(__name__)
CORS(app)
requestIDSeed = random.randint(0, 10000)
graphBatchGetter = GraphSeriesBatch()
recordDataGetter = RecordDataForUser()


@app.route('/')
def index():
    return 'ok'


@app.route('/api/init', methods=['POST'])
def init():
    global requestIDSeed
    requestIDSeed += 1
    tickets = request.get_json()["tickets"]
    task = spawnRequest.delay(tickets, requestIDSeed)
    return {"taskid": task.id, "requestid": requestIDSeed}


@app.route('/poll/progress/<taskID>')
def getRequestState(taskID):
    task = spawnRequest.AsyncResult(taskID)
    if task.ready():
        response = {
            'state': task.result.get('state'),
            'numRecords': task.result.get('numRecords')
        }
    else:
        if task.info.get('progress') is None:
            print('no progress')
        response = {
            'state': task.state,
            'progress': task.info.get('progress', 0)
        }
    return response


@app.route('/api/revokeTask/<taskID>/<reqID>')
def revokeTask(taskID, reqID):
    task = spawnRequest.AsyncResult(taskID)
    task.revoke(terminate=True)
    RecordDataForUser().clearUserRecordsAfterCancel(reqID)
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


@app.route('/api/numPapersOverRange/<startDate>/<endDate>')
def numPapersOverRange(startDate, endDate):
    search = PaperLocalSearch()
    numPapers = search.getNumPapersInRange(
        startDate,
        endDate
    )
    return {'numPapersOverRange': numPapers}


@app.route('/api/continuousPapers')
def getContinuousPapersOverRange():
    limit = request.args.get('limit')
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    search = PaperLocalSearch()
    selectPapers = search.selectPapersContinuousOverRange(
        startDate,
        endDate,
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
        'startDate': request.args["startDate"],
        'endDate': request.args["endDate"],
        'requestID': request.args["requestID"]
    }
    items = {'series': graphBatchGetter.getSeriesForSettings(settings)}
    return items


@app.route('/api/topPapers')
def getTopPapersFromID():
    ticketIDS = tuple(request.args["tickets"].split(","))
    topPapers = RecordDataForUser().getTopPapers(
        tickets=ticketIDS,
        requestID=request.args["requestID"],
    )
    items = {"topPapers": topPapers}
    return items


@app.route('/api/getcsv')
def getCSV():
    tickets = request.args["tickets"]
    requestID = request.args["requestID"]
    csvData = RecordDataForUser().getCSVData(tickets, requestID)
    return {"csvData": csvData}


@app.route('/api/getDisplayRecords')
def getDisplayRecords():
    tableArgs = dict(request.args)
    del tableArgs['uniqueforcache']
    tableArgs['tickets'] = tuple(tableArgs['tickets'].split(','))
    displayRecords, count = RecordDataForUser().getRecordsForDisplay(tableArgs)
    return {
        "displayRecords": displayRecords,
        "count": count
    }


@app.route('/api/getGallicaRecords')
def getGallicaRecordsForDisplay():
    args = dict(request.args)
    ticket = json.loads(args['tickets'])
    del args['tickets']
    records = recordDataGetter.getGallicaRecordsForDisplay(
        ticket=ticket,
        filters=args
    )
    records = [record.getDisplayRow() for record in records]
    return {"displayRecords": records}


@app.route('/api/ocrtext/<arkCode>/<term>')
def getOCRtext(arkCode, term):
    numResults, text = RecordDataForUser().getOCRTextForRecord(
        arkCode,
        term
    )
    return {"numResults": numResults, "text": text}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')