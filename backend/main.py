from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from tasks import spawn_request
from database.connContext import build_db_conn
from database.paperSearchResolver import (
    select_papers_similar_to_keyword,
    get_num_papers_in_range,
)
from database.graphDataResolver import select_series_for_tickets
from database.displayDataResolvers import (
    select_display_records,
    get_gallica_records_for_display,
    clear_records_for_requestid,
    get_ocr_text_for_record,
    select_csv_data_for_tickets,
    select_top_papers_for_tickets
)
from gallicaGetter.parse.volumeRecords import VolumeRecord
from gallicaGetter.parse.periodRecords import PeriodRecord

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


@app.get("/api/papers")
async def papers(keyword: str):
    with build_db_conn() as conn:
        similar_papers = select_papers_similar_to_keyword(keyword, conn)
    return similar_papers


@app.get("/api/numPapersOverRange")
async def get_num_papers_over_range(start: int, end: int):
    with build_db_conn() as conn:
        count = get_num_papers_in_range(
            start=start,
            end=end,
            conn=conn
        )
    return str(count)


@app.get('/api/graphData')
def get_graph_series_for_tickets(
        ticket_ids: int | List[int],
        request_id: int,
        grouping: Optional[str] = 'year',
        average_window: Optional[int] = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
):
    with build_db_conn() as conn:
        items = select_series_for_tickets(
            ticket_ids=ticket_ids,
            request_id=request_id,
            grouping=grouping,
            average_window=average_window,
            start_date=start_date,
            end_date=end_date,
            conn=conn
        )
    return {'series': items}


@app.get('/api/topPapers')
def get_top_papers(tickets: int | List[int], request_id: int, num_results: int = 10):
    with build_db_conn() as conn:
        top_papers = select_top_papers_for_tickets(
            tickets=tickets,
            requestID=request_id,
            num_results=num_results,
            conn=conn
        )
    return {"topPapers": top_papers}


@app.get('/api/getcsv')
def get_csv(tickets: int | List[int], requestID: int):
    with build_db_conn() as conn:
        csv_data = select_csv_data_for_tickets(
            tickets=tickets,
            requestID=requestID,
            conn=conn
        )
    return {"csvData": csv_data}


@app.get('/api/getDisplayRecords')
def records(
        ticketID: int | List[int],
        requestID: int,
        term: str = None,
        periodical: str = None,
        year: int = None,
        month: int = None,
        day: int = None
):
    with build_db_conn() as conn:
        records, count = select_display_records(
            tickets=ticketID,
            requestID=requestID,
            term=term,
            periodical=periodical,
            year=year,
            month=month,
            day=day,
            conn=conn
        )
    return {
        "displayRecords": records,
        "count": count
    }


@app.get('/api/getGallicaRecords')
def fetch_gallica_records(
        terms: str | List[str],
        codes: str | List[str] = None,
        start_date: int = None,
        link_term: str = None,
        link_distance: str = None,
        num_results: int = None,
        start_index: int = None
):
    records = get_gallica_records_for_display(
        terms=terms,
        codes=codes,
        start_date=start_date,
        link_term=link_term,
        link_distance=link_distance,
        num_results=num_results,
        start_index=start_index
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


@app.get('/api/ocrtext')
def ocr_text(ark_code: int, term: str):
    record = get_ocr_text_for_record(
        ark_code=ark_code,
        term=term
    )
    return {"numResults": record.num_results, "text": record.pages}
