import os
import uvicorn
import random
from typing import Dict, Literal
from pydantic import BaseModel
from www.database.connContext import build_db_conn
from www.database.graphDataResolver import build_highcharts_series
from www.request import Request
from www.models import Ticket, Progress
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
request_progress: Dict[int, Progress] = {}


@app.get("/")
def index():
    return {"message": "ok"}

@app.post("/api/init")
def init(ticket: Ticket):
    global requestID
    global request_progress

    def handle_update_progress(progress: Progress):
        request_progress[requestID] = progress

    requestID += 1
    request = Request(
        ticket=ticket,
        id=requestID,
        on_update_progress=handle_update_progress,
    )
    request.start()
    return {"requestid": requestID}


@app.get("/poll/progress/{request_id}")
def poll_request_state(request_id: int):
    global request_progress
    current_progress = request_progress.get(int(request_id))
    if current_progress and current_progress.state == "completed":
        del request_progress[int(request_id)]
    return current_progress


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
                    WHERE LOWER(title) LIKE %(paper_name)s
                    ORDER BY title DESC LIMIT 20;
            """,
                {"paper_name": "%" + keyword + "%"},
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
