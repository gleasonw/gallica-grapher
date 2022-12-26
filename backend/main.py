from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional


app = FastAPI()
requestID = 0


@app.get("/")
def index():
    return {"message": "Hello World"}


class Ticket(BaseModel):
    terms: List[str] | str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    codes: Optional[List[str] | str] = None
    grouping: str = 'year'
    generate: bool = False
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None


@app.post("/api/init")
def init(ticket: Ticket):
    global requestID
    requestID += 1
    print(ticket)
    return {"taskid": requestID, "requestid": requestID}


@app.get("/poll/progress/{task_id}")
def get_request_state(task_id: int):
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


@app.get("api/revokeTask/{celery_task_id}/{request_id}")
async def revoke_task(celery_task_id: int, request_id: int):
    with build_db_conn() as conn:
        task = spawn_request.AsyncResult(celery_task_id)
        task.revoke(terminate=True)
        clear_records_for_requestid(request_id, conn)
    return {'state': "REVOKED"}


@app.get("/api/papers/{keyword")
async def papers(keyword: str):
    with build_db_conn() as conn:
        similar_papers = select_papers_similar_to_keyword(keyword, conn)
    return similar_papers


@app.get("/api/numPapersOverRange/{start}/{end}")
async def get_num_papers_over_range(start: int, end: int):
    with build_db_conn() as conn:
        count = get_num_papers_in_range(
            start,
            end,
            conn
        )
    return str(count)


@app.get('/api/graphData')
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
    with build_db_conn() as conn:
        items = select_series_for_tickets(settings, conn)
    return {'series': items}


@app.get('/api/topPapers')
def get_top_papers():
    ticket_ids = tuple(request.args["tickets"].split(","))
    with build_db_conn() as conn:
        top_papers = select_top_papers_for_tickets(
            tickets=ticket_ids,
            requestID=request.args["requestID"],
            conn=conn
        )
    return {"topPapers": top_papers}


@app.get('/api/getcsv')
def get_csv():
    tickets = request.args["tickets"]
    request_id = request.args["requestID"]
    with build_db_conn() as conn:
        csv_data = select_csv_data_for_tickets(
            tickets,
            request_id,
            conn=conn
        )
    return {"csvData": csv_data}


@app.get('/api/getDisplayRecords')
def records():
    table_filters = dict(request.args)
    table_filters['tickets'] = tuple(table_filters['tickets'].split(','))
    with build_db_conn() as conn:
        records, count = select_display_records(table_filters, conn)
    return {
        "displayRecords": records,
        "count": count
    }
    
    #TODO: add request params
@app.get('/api/getGallicaRecords')
def fetch_gallica_records(terms: str | List[str], start_date: int = None, codes: str | List[str], link_term: str=None, link_distance: str=None, num_results: int=None, start_index: int=None):
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
    records = get_gallica_records_for_display(
        tickets=tickets,
        limit=args['limit'],
        offset=args['offset'],
    )
    display_records = []
    if records:
        # a procedural implementation. I feel records should not know how they are displayed
        if isinstance(records[0], VolumeRecord):
            for volume_occurrence in records:
                display_records.append(
                    (
                        volume_occurrence.term,
                        volume_occurrence.paper_title,
                        volume_occurrence.date.getYear(),
                        volume_occurrence.date.getMonth(),
                        volume_occurrence.date.getDay(),
                        volume_occurrence.url
                    )
                )
        elif isinstance(records[0], PeriodRecord):
            for period_record in records:
                display_records.append(
                    (
                        period_record.term,
                        period_record.date.getYear(),
                        period_record.date.getMonth(),
                        period_record.date.getDay(),
                        period_record.count
                    )
                )
        else:
            raise ValueError(f"Unknown record type: {type(records[0])}")
    return {"displayRecords": display_records}
