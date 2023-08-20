import os
from starlette import status
import uvicorn
from typing import Literal
from pydantic import BaseModel
from fastapi import BackgroundTasks, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import datetime
from typing import List, Literal, Tuple
import backend.gallicagram as gallicagram
import os
import pymysql
import dotenv

dotenv.load_dotenv()


import ciso8601

from backend.models import PeriodRecord, Series, Ticket
import gallicagram

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "ok"}


class Paper(BaseModel):
    title: str
    code: str
    start_date: str
    end_date: str


class MySQL:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.environ.get("HOST"),
            user=os.environ.get("USERNAME"),
            password=os.environ.get("PASSWORD"),
            database=os.environ.get("DATABASE"),
            ssl={"ca": "/etc/ssl/certs/ca-certificates.crt"},
        )

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


@app.get("/api/papers/{keyword}")
def papers(keyword: str):
    """Paper search dropdown route"""
    with MySQL() as conn:
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
    with MySQL() as conn:
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


def insert_series(records: List[PeriodRecord], conn):
    with conn.cursor() as curs:
        curs.executemany(
            """
            INSERT INTO groupcounts (year, month, term, count)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                (
                    record.year,
                    record.month,
                    record.term,
                    record.count,
                )
                for record in records
            ],
        )


@app.get("/api/graphData")
async def graph_data(
    term: str,
    year: int,
    end_year: int,
    response: Response,
    background_tasks: BackgroundTasks,
    grouping: Literal["month", "year"] = "year",
    smoothing: int = 0,
):
    with MySQL() as conn:
        all_data_in_db = False
        with conn.cursor() as curs:
            curs.execute(
                """
                SELECT count
                FROM series
                WHERE term = %s
                AND year >= %s
                AND year <= %s
                """,
                (term, year, end_year),
            )
            series_in_db = curs.fetchall()
            if len(series_in_db) == ((year - end_year) + 1) * 12:
                all_data_in_db = True
        if not all_data_in_db:

            def no_records_found():
                response.status_code = status.HTTP_204_NO_CONTENT
                return

            if pyllica_records := await gallicagram.get(
                Ticket(
                    term=term,
                    year=year,
                    end_year=end_year,
                ),
                on_no_records_found=no_records_found,
            ):
                records = list(pyllica_records)
                background_tasks.add_task(insert_series, records, conn)
                data_with_db_format = [
                    (record.year, record.month, record.day, record.count)
                    for record in records
                ]
                data_with_proper_date_format = [
                    get_row_timestamp(row) for row in data_with_db_format
                ]
                if smoothing:
                    data_with_proper_date_format = get_moving_average(
                        data_with_proper_date_format, smoothing
                    )
                return Series(name=term, data=data_with_proper_date_format)

            else:
                no_records_found()

        return build_highcharts_series(
            term=term,
            year=year,
            end_year=end_year,
            grouping=grouping,
            smoothing=smoothing,
            conn=conn,
        )


def build_highcharts_series(
    term: str,
    year: int,
    end_year: int,
    grouping: Literal["month", "year"],
    smoothing: int,
    conn,
) -> Series:
    if grouping == "year":
        sql = """
            SELECT year, sum(count) as count
            FROM series
            WHERE term = %s
            AND year >= %s
            AND year <= %s
            GROUP BY year
            ORDER BY year;
        """
    elif grouping == "month":
        sql = """
            SELECT year, month, sum(count) as count
            FROM series
            WHERE term = %s
            AND year >= %s
            AND year <= %s
            GROUP BY year, month
            ORDER BY year, month;
        """
    else:
        raise ValueError(f"Invalid grouping: {grouping}")
    with conn.cursor() as curs:
        curs.execute(sql, (term, year, end_year))
        data = curs.fetchall()

    data_with_proper_date_format = list(map(get_row_timestamp, data))
    if smoothing:
        data_with_proper_date_format = get_moving_average(
            data_with_proper_date_format, smoothing
        )
    return Series(name=term, data=data_with_proper_date_format)


def get_moving_average(
    data: List[Tuple[float, float]], window: int
) -> List[Tuple[float, float]]:
    unpacked_data = [x for x in data]
    for i in range(1, len(unpacked_data)):
        if i < window:
            window_data = data[:i]
        else:
            window_data = data[i - window : i]
        window_data = [x[1] for x in window_data]
        average = sum(window_data) / len(window_data)
        unpacked_data[i] = (unpacked_data[i][0], average)
    return unpacked_data


def get_row_timestamp(row: Tuple) -> Tuple[float, float]:
    if len(row) == 4:
        year = row[0]
        month = row[1]
        day = row[2]
        frequency = row[3]
        date = f"{year}-{month:02d}-{day:02d}"
        unix_seconds = get_timestamp(date)
    elif len(row) == 3:
        year = row[0]
        month = row[1]
        frequency = row[2]
        date = f"{year}-{month:02d}-01"
        unix_seconds = get_timestamp(date)
    elif len(row) == 2:
        year = row[0]
        frequency = row[1]
        date = f"{year}-01-01"
        unix_seconds = get_timestamp(date)
    else:
        raise ValueError(f"Invalid row: {row}")
    return (unix_seconds, frequency)


def get_timestamp(date: str):
    date_object = ciso8601.parse_datetime(date)
    date_object = date_object.replace(tzinfo=datetime.timezone.utc)
    return datetime.datetime.timestamp(date_object) * 1000


if __name__ == "__main__":
    print("Running on port", os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
