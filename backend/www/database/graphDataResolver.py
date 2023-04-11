import datetime
from typing import List, Literal, Tuple

import ciso8601

from www.models import (
    Series,
)


def build_highcharts_series(
    request_id: int,
    grouping: Literal["day", "month", "year"],
    backend_source: Literal["gallica", "pyllica"],
    average_window: int,
    conn,
) -> Series:
    data = get_from_db(
        params=(request_id,),
        sql=get_sql_for_grouping(grouping, backend_source),
        conn=conn,
    )
    data_with_proper_date_format = list(map(get_row_timestamp, data))
    if average_window:
        data_with_proper_date_format = get_moving_average(
            data_with_proper_date_format, average_window
        )
    search_terms = get_search_terms_by_grouping(
        backend_source=backend_source, request_id=request_id, conn=conn
    )
    if search_terms and len(search_terms) == 1:
        search_terms = search_terms[0]
    return Series(
        name=f"{search_terms}", data=data_with_proper_date_format, request_id=request_id
    )


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


def get_sql_for_grouping(
    grouping: Literal["day", "month", "year"],
    backend_source: Literal["gallica", "pyllica"],
):
    match (grouping, backend_source):
        case ("year", "pyllica"):
            return """
            SELECT year, sum(count) as count
            FROM groupcounts
            WHERE requestid = %s
            GROUP BY year
            ORDER BY year;
            """
        case ("month", "pyllica"):
            return """
            SELECT year, month, sum(count) as count
            FROM groupcounts
            WHERE requestid = %s
            GROUP BY year, month
            ORDER BY year, month;
            """
        case _:
            raise ValueError(
                f"Invalid grouping/backend_source: {grouping}/{backend_source}"
            )


def get_search_terms_by_grouping(
    backend_source: Literal["gallica", "pyllica"],
    request_id: int,
    conn,
):
    table = "FROM results" if backend_source == "gallica" else "FROM groupcounts"

    get_terms = f"""
        SELECT group_concat(DISTINCT searchterm) 
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
