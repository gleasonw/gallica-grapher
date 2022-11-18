from flask import Flask
from flask import request
from flask_cors import CORS
import random
import json
from tasks import spawn_request
from database.connContext import build_db_conn
from database.paperSearchResolver import (
    select_continuous_papers,
    get_papers_similar_to_keyword,
    get_num_papers_in_range,
)
from database.graphDataResolver import get_series_for_tickets
from database.displayDataResolvers import (
    select_display_records,
    get_gallica_records_for_display,
    clear_records_for_requestid,
    get_ocr_text_for_record,
    get_csv_data_for_request,
    get_top_papers_for_tickets
)
import time

app = Flask(__name__)
CORS(app)
requestIDSeed = random.randint(0, 10000)


@app.route('/')
def index():
    return 'ok'


@app.route('/api/init', methods=['POST'])
def init():
    global requestIDSeed
    requestIDSeed += 1
    tickets = request.get_json()["tickets"]
    task = spawn_request.delay(tickets, requestIDSeed)
    return {"taskid": task.id, "requestid": requestIDSeed}


@app.route('/poll/progress/<task_id>')
def get_request_state(task_id):
    task = spawn_request.AsyncResult(task_id)
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


@app.route('/api/revokeTask/<celery_task_id>/<request_id>')
def revoke_task(celery_task_id, request_id):
    with build_db_conn() as conn:
        task = spawn_request.AsyncResult(celery_task_id)
        task.revoke(terminate=True)
        clear_records_for_requestid(request_id, conn)
    return {'state': "REVOKED"}


@app.route('/api/papers/<keyword>')
def papers(keyword):
    with build_db_conn() as conn:
        similar_papers = get_papers_similar_to_keyword(keyword, conn)
    return similar_papers


@app.route('/api/numPapersOverRange/<start>/<end>')
def get_num_papers_publishing_in_range(start, end):
    with build_db_conn() as conn:
        count = get_num_papers_in_range(
            start,
            end,
            conn
        )
    return {'numPapersOverRange': count}


@app.route('/api/continuousPapers')
def get_continuous_papers_for_range():
    limit = request.args.get('limit')
    start = request.args.get('startDate')
    end = request.args.get('endDate')
    with build_db_conn() as conn:
        continuous_papers = select_continuous_papers(
            start,
            end,
            limit,
            conn
        )
    return continuous_papers


@app.route('/api/graphData')
def get_graph_series_for_tickets():
    settings = {
        'ticketIDs': request.args["keys"],
        'averageWindow': request.args["averageWindow"],
        'groupBy': request.args["timeBin"],
        'continuous': request.args["continuous"],
        'startDate': request.args["startDate"],
        'endDate': request.args["endDate"],
        'requestID': request.args["requestID"]
    }
    start = time.perf_counter()
    with build_db_conn() as conn:
        items = get_series_for_tickets(settings, conn)
    end = time.perf_counter()
    print(f"get_series_for_tickets {request.args['requestID']} took {end - start} seconds")
    return {'series': items}


@app.route('/api/topPapers')
def get_top_papers():
    ticket_ids = tuple(request.args["tickets"].split(","))
    start = time.perf_counter()
    with build_db_conn() as conn:
        top_papers = get_top_papers_for_tickets(
            tickets=ticket_ids,
            requestID=request.args["requestID"],
            conn=conn
        )
    end = time.perf_counter()
    print(f"get_top_papers_for_tickets {request.args['requestID']} took {end - start} seconds")
    return {"topPapers": top_papers}


@app.route('/api/getcsv')
def get_csv():
    tickets = request.args["tickets"]
    request_id = request.args["requestID"]
    with build_db_conn() as conn:
        csv_data = get_csv_data_for_request(
            tickets,
            request_id,
            conn=conn
        )
    return {"csvData": csv_data}


@app.route('/api/getDisplayRecords')
def get_display_records():
    table_filters = dict(request.args)
    table_filters['tickets'] = tuple(table_filters['tickets'].split(','))
    start= time.perf_counter()
    with build_db_conn() as conn:
        records, count = select_display_records(table_filters, conn)
    end = time.perf_counter()
    print(f"select_display_records {request.args['requestID']} took {end - start} seconds")
    return {
        "displayRecords": records,
        "count": count
    }


#TODO: enlist celery worker to make request async -- flask blocks while responding to this
#TODO: clarify arguments
@app.route('/api/getGallicaRecords')
def fetch_gallica_records():
    """
    Fetches a batch of volume occurrence records from Gallica.

    Params are passed in the query string like so:
    /api/getGallicaRecords?tickets=[{"terms":["brazza"],"grouping":"all","startDate":"1899","codes":[]}]&limit=5&offset=0

    :param tickets: JSON-encoded array of search parameters:
        :param terms: a list of search terms,
        :param startDate: start date for the search,
        :param codes: periodicals to restrict search (optional),
        :param linkTerm: link for proximity search (optional),
        :param linkDistance: distance for proximity search (optional),
    :param limit: number of records to fetch
    :param offset: offset for the records to fetch

    :return: List[(terms, periodical, year, month, day, gallica url)...]
    """
    args = dict(request.args)
    tickets = json.loads(args['tickets'])
    start= time.perf_counter()
    records = get_gallica_records_for_display(
        tickets=tickets,
        limit=args['limit'],
        offset=args['offset'],
    )
    end = time.perf_counter()
    print(f"get_gallica_records_for_display {request.args['requestID']} took {end - start} seconds")
    records = [record.getDisplayRow() for record in records]
    return {"displayRecords": records}


@app.route('/api/ocrtext/<ark_code>/<term>')
def get_ocr_text(ark_code, term):
    record = get_ocr_text_for_record(
        ark_code,
        term
    )
    return {"numResults": record.num_results, "text": record.get_pages()}


if __name__ == "__main__":
    app.run()
