from typing import List, Optional, Literal

from fastapi import FastAPI

from database.connContext import build_db_conn
from database.displayDataResolvers import (
    select_display_records,
    get_gallica_records_for_display,
    clear_records_for_requestid,
    get_ocr_text_for_record,
    select_csv_data_for_tickets,
    select_top_papers_for_tickets
)
from database.graphDataResolver import select_series_for_tickets
from database.paperSearchResolver import (
    select_papers_similar_to_keyword,
    get_num_papers_in_range,
)
from gallicaGetter.parse.periodRecords import PeriodRecord
from gallicaGetter.parse.volumeRecords import VolumeRecord
from tasks import spawn_request
from ticket import Ticket

app = FastAPI()
requestID = 0


@app.get("/")
def index():
    return {"message": "ok"}


@app.post("/api/init")
def init(ticket: Ticket | List[Ticket]):
    global requestID
    requestID += 1
    print(ticket)
    task = spawn_request.delay(ticket, requestID)
    return {"taskid": task.id, "requestid": requestID}


@app.get("/poll/progress/{task_id}")
def poll_request_state(task_id: int):
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
def revoke_task(celery_task_id: int, request_id: int):
    with build_db_conn() as conn:
        task = spawn_request.AsyncResult(celery_task_id)
        task.revoke(terminate=True)
        clear_records_for_requestid(request_id, conn)
    return {'state': "REVOKED"}


@app.get("/api/papers/{keyword}")
def papers(keyword: str):
    with build_db_conn() as conn:
        similar_papers = select_papers_similar_to_keyword(keyword, conn)
    return similar_papers


@app.get("/api/numPapersOverRange/{start}/{end}")
def get_num_papers_over_range(start: int, end: int):
    with build_db_conn() as conn:
        count = get_num_papers_in_range(
            start=start,
            end=end,
            conn=conn
        )
    return str(count)


@app.get('/api/graphData')
def graph_data(
        ticket_ids: int | List[int],
        request_id: int,
        grouping: Literal["day", "month", "year", "gallicaMonth", "gallicaYear"] = 'year',
        average_window: Optional[int] = 0,
):
    with build_db_conn() as conn:
        items = select_series_for_tickets(
            ticket_ids=ticket_ids,
            request_id=request_id,
            grouping=grouping,
            average_window=average_window,
            conn=conn
        )
    return {'series': items}


@app.get('/api/topPapers')
def get_top_papers(tickets: int | List[int], request_id: int, num_results: int = 10):
    with build_db_conn() as conn:
        top_papers = select_top_papers_for_tickets(
            tickets=tickets,
            request_id=request_id,
            num_results=num_results,
            conn=conn
        )
    return {"topPapers": top_papers}


@app.get('/api/getcsv')
def get_csv(tickets: int | List[int], request_id: int):
    with build_db_conn() as conn:
        csv_data = select_csv_data_for_tickets(
            ticket_ids=tickets,
            request_id=request_id,
            conn=conn
        )
    return {"csvData": csv_data}


@app.get('/api/getDisplayRecords')
def records(
        ticket_ids: int | List[int],
        request_id: int,
        term: str = None,
        periodical: str = None,
        year: int = None,
        month: int = None,
        day: int = None,
        limit: int = 10,
        offset: int = 0
):
    with build_db_conn() as conn:
        db_records, count = select_display_records(
            ticket_ids=ticket_ids,
            request_id=request_id,
            term=term,
            periodical=periodical,
            limit=limit,
            offset=offset,
            year=year,
            month=month,
            day=day,
            conn=conn
        )
    return {
        "displayRecords": db_records,
        "count": count
    }


@app.get('/api/getGallicaRecords')
def fetch_records_from_gallica(tickets: Ticket | List[Ticket]):
    gallica_records = get_gallica_records_for_display(tickets)
    if gallica_records:
        # a procedural implementation. I feel records should not know how they should be displayed
        if isinstance(gallica_records[0], VolumeRecord):
            display_records = [
                (
                    volume_occurrence.term,
                    volume_occurrence.paper_title,
                    volume_occurrence.date.getYear(),
                    volume_occurrence.date.getMonth(),
                    volume_occurrence.date.getDay(),
                    volume_occurrence.url
                )
                for volume_occurrence in gallica_records
            ]
        elif isinstance(gallica_records[0], PeriodRecord):
            display_records = [
                (
                    period_record.term,
                    period_record.date.getYear(),
                    period_record.date.getMonth(),
                    period_record.date.getDay(),
                    period_record.count
                )
                for period_record in gallica_records
            ]
        else:
            raise ValueError(f"Unknown record type: {type(gallica_records[0])}")
    else:
        display_records = []
    return {"displayRecords": display_records}


@app.get('/api/ocrtext/{ark_code}/{term}')
def ocr_text(ark_code: int, term: str):
    record = get_ocr_text_for_record(
        ark_code=ark_code,
        term=term
    )
    return {"numResults": record.num_results, "text": record.pages}
