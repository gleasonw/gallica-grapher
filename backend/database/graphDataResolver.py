import datetime
from typing import Literal, Tuple

import ciso8601

from database.series import (
    Series,
    SeriesDataPoint,
)


def build_highcharts_series(
    request_id: int,
    grouping: Literal["day", "month", "year"],
    backend_source: Literal["gallica", "pyllica"],
    average_window: int,
    conn,
) -> Series:
    # TODO: why on earth does the order matter?
    if backend_source == "gallica":
        psycop_params = (request_id, average_window)
    elif backend_source == "pyllica":
        psycop_params = (average_window, request_id)
    else:
        raise ValueError(f"Invalid backend_source: {backend_source}")
    data = get_from_db(
        params=psycop_params,
        sql=get_sql_for_grouping(grouping, backend_source),
        conn=conn,
    )
    if grouping == "day":
        data_with_proper_date_format = list(map(get_rows_ymd_timestamp, data))
    elif grouping == "month":
        data_with_proper_date_format = list(map(get_rows_ym_timestamp, data))
    elif grouping == "year":
        data_with_proper_date_format = data
    else:
        raise ValueError(f"Invalid grouping: {grouping}")
    search_terms = get_search_terms_by_grouping(
        backend_source=backend_source, request_id=request_id, conn=conn
    )
    data_as_points = [
        SeriesDataPoint(
            date=point[0],
            count=point[1],
        )
        for point in data_with_proper_date_format
    ]
    return Series(name=f"{search_terms}", data=data_as_points, request_id=request_id)


def get_sql_for_grouping(
    grouping: Literal["day", "month", "year"],
    backend_source: Literal["gallica", "pyllica"],
):
    match (grouping, backend_source):
        case ("day", "gallica"):
            return """

            WITH binned_frequencies AS (
                SELECT year, month, day, count(*) AS mentions 
                FROM results 
                WHERE requestid = %s
                AND month IS NOT NULL
                AND day IS NOT NULL
                GROUP BY year, month, day 
                ORDER BY year, month, day),

                averaged_frequencies AS (
                SELECT year, month, day, AVG(mentions) 
                OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM binned_frequencies)

            SELECT year, month, day, avgFrequency::float8
            FROM averaged_frequencies;

            """
        case ("month", "gallica"):
            return """

            WITH binned_frequencies AS
                (SELECT year, month, count(*) AS mentions 
                FROM results continuous
                WHERE requestid = %s
                AND month IS NOT NULL
                GROUP BY year, month
                ORDER BY year,month),

                averaged_frequencies AS 
                (SELECT year, month, 
                        AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM binned_frequencies)

            SELECT year, month, avgFrequency::float8 
            FROM averaged_frequencies;
            
            """
        case ("year", "gallica"):
            return """

            WITH binned_frequencies AS
                (SELECT year, count(*) AS mentions 
                FROM results 
                WHERE requestid=%s
                GROUP BY year 
                ORDER BY year),

                averaged_frequencies AS
                (SELECT year, 
                        AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM binned_frequencies)

            SELECT year, avgFrequency::float8
            FROM averaged_frequencies;
            
            """
        case ("year", "pyllica"):
            return """
            
            SELECT year, avgFrequency::float8 
            FROM (
                SELECT year, AVG(count) 
                OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM (
                    SELECT year, sum(count) as count
                    FROM groupcounts
                    WHERE requestid = %s
                    GROUP BY year
                    ORDER BY year
                ) AS counts
            ) AS avgedCounts;
            
            """
        case ("month", "pyllica"):
            return """
            
            SELECT year, month, avgFrequency::float8
            FROM (
                SELECT year, month, AVG(count) 
                OVER (ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM (
                    SELECT year, month, sum(count) as count
                    FROM groupcounts
                    WHERE requestid = %s
                    GROUP BY year, month
                    ORDER BY year, month
                ) AS counts
            ) AS avgedCounts;
            
            """


def get_search_terms_by_grouping(
    backend_source: Literal["gallica", "pyllica"],
    request_id: int,
    conn,
):
    table = "FROM results" if backend_source == "gallica" else "FROM groupcounts"

    get_terms = f"""
        SELECT array_agg(DISTINCT searchterm) 
        {table}
        WHERE requestid=%s 
        """

    with conn.cursor() as curs:
        curs.execute(get_terms, (request_id,))
        return curs.fetchone()[0]


def get_from_db(conn, params: Tuple, sql: str):
    with conn.cursor() as curs:
        curs.execute(sql, params)
        return curs.fetchall()


def get_rows_ymd_timestamp(row):
    year = row[0]
    month = row[1]
    day = row[2]
    frequency = row[3]
    date = f"{year}-{month:02d}-{day:02d}"
    return get_timestamp(date), frequency


def get_rows_ym_timestamp(row):
    year = row[0]
    month = row[1]
    frequency = row[2]
    date = f"{year}-{month:02d}-01"
    return get_timestamp(date), frequency


def get_timestamp(date):
    try:
        date_object = ciso8601.parse_datetime(date)
        date_object = date_object.replace(tzinfo=datetime.timezone.utc)
        timestamp = datetime.datetime.timestamp(date_object) * 1000
    except ValueError:
        print(f"erred with date: {date}")
        return None
    return timestamp


def get_params_for_ticket_and_settings(settings):
    if settings["continuous"] == "true":
        return (
            settings["requestID"],
            settings["startDate"],
            settings["endDate"],
            settings["averageWindow"],
        )
    elif settings["groupBy"] in ["gallicaYear", "gallicaMonth"]:
        return settings["averageWindow"], settings["requestID"]
    else:
        return settings["requestID"], settings["averageWindow"]
