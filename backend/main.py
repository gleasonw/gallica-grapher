import json
import os
import random
from typing import List, Literal, Optional
import uvicorn
from pydantic import BaseModel
from gallicaGetter.contentWrapper import GallicaContext
import gallicaGetter.wrapperFactory as wF
from www.database.connContext import build_db_conn, build_redis_conn
from www.database.graphDataResolver import build_highcharts_series
from www.database.displayDataResolvers import (
    make_date_from_year_mon_day,
    select_display_records,
)
from www.request import Request
from www.models import Ticket, Progress
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

requestID = random.randint(0, 1000000000)


@app.get("/")
def index():
    return {"message": "ok"}


@app.post("/api/init")
def init(ticket: Ticket):
    global requestID
    requestID += 1
    ticket.id = requestID
    with build_redis_conn() as redis_conn:
        redis_conn.delete(f"request:{requestID}:progress")
        redis_conn.delete(f"request:{requestID}:cancelled")
    request = Request(ticket=ticket)
    request.start()
    return {"requestid": requestID}


@app.get("/poll/progress/{request_id}")
def poll_request_state(request_id: str):
    with build_redis_conn() as redis_conn:
        progress = redis_conn.get(f"request:{request_id}:progress")
        if progress:
            progress = json.loads(progress)
            progress = Progress(**progress)
        else:
            progress = Progress(
                num_results_discovered=0,
                num_requests_to_send=0,
                num_requests_sent=0,
                estimate_seconds_to_completion=0,
                random_paper="",
                random_text="",
                state="running",
                backend_source="gallica",
            )
    return progress


class Paper(BaseModel):
    title: str
    code: str
    start_date: str
    end_date: str


@app.get("/api/papers/{keyword}")
def papers(keyword: str):
    """Paper search dropdown route"""
    with build_db_conn() as conn:
        keyword = keyword.lower()
        with conn.cursor() as curs:
            curs.execute(
                """
                SELECT title, code, startdate, enddate
                    FROM papers 
                    WHERE LOWER(title) LIKE %(paperNameSearchString)s
                    ORDER BY title DESC LIMIT 20;
            """,
                {"paperNameSearchString": "%" + keyword + "%"},
            )
            similar_papers = curs.fetchall()
            papers = [
                Paper(
                    title=paper[0],
                    code=paper[1],
                    start_date=paper[2],
                    end_date=paper[3],
                )
                for paper in similar_papers
            ]
    return {"papers": papers}


@app.get("/api/numPapersOverRange/{start}/{end}")
def get_num_papers_over_range(start: int, end: int):
    """Number of papers that published in a year between start and end."""
    with build_db_conn() as conn:
        with conn.cursor() as curs:
            curs.execute(
                """
                SELECT COUNT(*) FROM papers
                    WHERE startdate BETWEEN %s AND %s
                        OR enddate BETWEEN %s AND %s
                        OR (startdate < %s AND enddate > %s)
                    ;
                """,
                (start, end, start, end, start, end),
            )
            num_papers_over_range = curs.fetchone()
        count = num_papers_over_range and num_papers_over_range[0]
    return count


@app.get("/api/graphData")
def graph_data(
    request_id: int,
    grouping: Literal["month", "year"] = "year",
    backend_source: Literal["gallica", "pyllica"] = "pyllica",
    average_window: int = 0,
):
    with build_db_conn() as conn:
        return build_highcharts_series(
            request_id=request_id,
            grouping=grouping,
            backend_source=backend_source,
            average_window=average_window,
            conn=conn,
        )


@app.get("/api/getDisplayRecords")
def records(
    request_id: int,
    ticket_ids: List[int] = Query(),
    term: str = "",
    periodical: str = "",
    year: int = 0,
    month: int = 0,
    day: int = 0,
    limit: int = 10,
    offset: int = 0,
):
    """Gets records stored in the database, as opposed to fetching them from Gallica."""
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
            conn=conn,
        )
    return {"displayRecords": db_records, "count": count}


class GallicaRecord(BaseModel):
    paper_title: str
    paper_code: str
    term: str
    date: str
    url: str
    context: GallicaContext


class GallicaResponse(BaseModel):
    records: List[GallicaRecord]
    num_results: int


@app.get("/api/gallicaRecords")
def fetch_records_from_gallica(
    year: Optional[int] = 0,
    month: Optional[int] = 0,
    day: Optional[int] = 0,
    terms: List[str] = Query(),
    codes: Optional[List[str]] = Query(None),
    cursor: Optional[int] = 0,
    limit: Optional[int] = 10,
    link_term: Optional[str] = None,
    link_distance: Optional[int] = 0,
    source: Literal["book", "periodical", "all"] = "all",
    sort: Literal["date", "relevance"] = "relevance",
) -> GallicaResponse:
    """API endpoint for the context table."""
    link = None
    if link_term and not link_distance or link_distance and not link_term:
        raise HTTPException(
            status_code=400,
            detail="link_distance and link_term must both be specified if either is specified",
        )
    if link_distance and link_term:
        link_distance = int(link_distance)
        link = (link_term, link_distance)

    total_records = 0

    def set_total_records(num_records: int):
        """Callback passed to the volume wrapper"""
        nonlocal total_records
        total_records = num_records

    # fetch the volumes in which terms appear
    volume_Gallica_wrapper = wF.WrapperFactory.volume()
    gallica_records = volume_Gallica_wrapper.get(
        terms=terms,
        start_date=make_date_from_year_mon_day(year, month, day),
        codes=codes,
        source=source,
        link=link,
        num_results=limit,
        start_index=cursor,
        sort=sort,
        on_get_total_records=set_total_records,
    )

    # fetch the context for those terms
    content_wrapper = wF.WrapperFactory.context()
    keyed_records = {record.url.split("/")[-1]: record for record in gallica_records}
    context = content_wrapper.get(
        [
            (record.url.split("/")[-1], record.term)
            for _, record in keyed_records.items()
        ]
    )

    # combine the two
    records_with_context: List[GallicaRecord] = []
    for record in context:
        corresponding_record = keyed_records[record.ark]
        records_with_context.append(
            GallicaRecord(
                paper_title=corresponding_record.paper_title,
                paper_code=corresponding_record.paper_code,
                term=corresponding_record.term,
                date=str(corresponding_record.date),
                url=corresponding_record.url,
                context=record,
            )
        )

    return GallicaResponse(records=records_with_context, num_results=total_records)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))