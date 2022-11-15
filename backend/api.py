from flask import Flask
from flask import request
from flask_cors import CORS
import random
import json
from database.graphDataResolver import GraphSeriesBatch
from tasks import spawnRequest
from database.displayDataResolvers import RecordDataForUser
from database.connContext import build_db_conn
from database.paperSearchResolver import (
    select_continuous_papers,
    get_papers_similar_to_keyword,
    get_num_papers_in_range,
)

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
    with build_db_conn() as conn:
        tickets = request.get_json()["tickets"]
        task = spawnRequest.delay(tickets, requestIDSeed, conn)
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
    with build_db_conn() as conn:
        task = spawnRequest.AsyncResult(taskID)
        task.revoke(terminate=True)
        clear_records_for_requestID(reqID, conn)
    return {'state': "REVOKED"}


@app.route('/api/papers/<keyword>')
def papers(keyword):
    with build_db_conn() as conn:
        similarPapers = get_papers_similar_to_keyword(keyword, conn)
    return similarPapers


@app.route('/api/numPapersOverRange/<startDate>/<endDate>')
def numPapersOverRange(startDate, endDate):
    with build_db_conn() as conn:
        numPapers = get_num_papers_in_range(
            startDate,
            endDate,
            conn
        )
    return {'numPapersOverRange': numPapers}


@app.route('/api/continuousPapers')
def getContinuousPapersOverRange():
    limit = request.args.get('limit')
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    with build_db_conn() as conn:
        selectPapers = select_continuous_papers(
            startDate,
            endDate,
            limit,
            conn
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
    with build_db_conn() as conn:
        items = get_series_for_settings(settings, conn)
    return {'series': items}


@app.route('/api/topPapers')
def getTopPapersFromID():
    ticketIDS = tuple(request.args["tickets"].split(","))
    with build_db_conn() as conn:
        topPapers = get_top_papers_for_tickets(
            tickets=ticketIDS,
            requestID=request.args["requestID"],
            conn=conn
        )
    return {"topPapers": topPapers}


@app.route('/api/getcsv')
def getCSV():
    tickets = request.args["tickets"]
    requestID = request.args["requestID"]
    with build_db_conn() as conn:
        csvData = get_csv_data_for_request(
            tickets,
            requestID,
            conn=conn
        )
    return {"csvData": csvData}


#TODO: enlist celery worker?
@app.route('/api/getDisplayRecords')
def getDisplayRecords():
    tableArgs = dict(request.args)
    tableArgs['tickets'] = tuple(tableArgs['tickets'].split(','))
    with build_db_conn() as conn:
        displayRecords, count = get_display_records(tableArgs, conn)
    return {
        "displayRecords": displayRecords,
        "count": count
    }


@app.route('/api/getGallicaRecords')
def getGallicaRecordsForDisplay():
    args = dict(request.args)
    tickets = json.loads(args['tickets'])
    del args['tickets']
    records = get_gallica_records_for_display(
        tickets=tickets,
        filters=args
    )
    records = [record.getDisplayRow() for record in records]
    return {"displayRecords": records}


@app.route('/api/ocrtext/<arkCode>/<term>')
def getOCRtext(arkCode, term):
    numResults, text = recordDataGetter.getOCRTextForRecord(
        arkCode,
        term
    )
    return {"numResults": numResults, "text": text}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')