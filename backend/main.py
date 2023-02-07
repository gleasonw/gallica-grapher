import json
import os
import random
from typing import List, Literal, Optional
import uvicorn
from pydantic import BaseModel
from gallicaContextSearch import UserResponse, get_row_context, get_html_context
import gallicaGetter.wrapperFactory as wF
from www.database.connContext import build_db_conn, build_redis_conn
from www.database.graphDataResolver import build_highcharts_series
from www.database.displayDataResolvers import select_display_records
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
    row_split: Optional[bool] = False,
) -> UserResponse:
    """API endpoint for the context table."""

    if limit and limit > 50:
        raise HTTPException(status_code=400, detail="Limit must be less than or equal to 50, the maximum number of records for one request to Gallica.")

    if row_split:
        return get_row_context(
            year=year,
            month=month,
            day=day,
            terms=terms,
            codes=codes,
            cursor=cursor,
            limit=limit,
            link_term=link_term,
            link_distance=link_distance,
            source=source,
            sort=sort,
        )
    return get_html_context(
            year=year,
            month=month,
            day=day,
            terms=terms,
            codes=codes,
            cursor=cursor,
            limit=limit,
            link_term=link_term,
            link_distance=link_distance,
            source=source,
            sort=sort,
    )



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
