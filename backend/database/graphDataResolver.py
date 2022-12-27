import datetime
from dataclasses import dataclass
from typing import List, Literal, Tuple

import ciso8601


def select_series_for_tickets(
        ticket_ids: int | List[int],
        request_id: int,
        grouping: Literal["day", "month", "year", "gallicaMonth", "gallicaYear"],
        average_window: int,
        conn
):
    batch_series = list(map(
        lambda ticket_id: build_highcharts_series(
            ticket_id=ticket_id,
            request_id=request_id,
            grouping=grouping,
            average_window=average_window,
            conn=conn
        ),
        ticket_ids
    ))
    return {
        series.ticket_id: series.data
        for series in batch_series
    }


@dataclass(slots=True, frozen=True)
class Series:
    ticket_id: int
    data: List[Tuple[int, float]]
    name: str


def build_highcharts_series(
        ticket_id: int,
        request_id: int,
        grouping: Literal["day", "month", "year", "gallicaMonth", "gallicaYear"],
        average_window: int,
        conn
) -> Series:
    if grouping == 'gallicaYear' or grouping == 'gallicaMonth':
        psycop_params = (
            average_window,
            request_id,
            ticket_id
        )
    else:
        psycop_params = (
            request_id,
            ticket_id,
            average_window
        )
    data = get_from_db(
        params=psycop_params,
        sql=get_sql_for_grouping(grouping),
        conn=conn
    )
    if grouping == 'day':
        data_with_proper_date_format = list(map(get_rows_ymd_timestamp, data))
    elif grouping == 'month' or grouping =='gallicaMonth':
        data_with_proper_date_format = list(map(get_rows_ym_timestamp, data))
    else:
        data_with_proper_date_format = data
    search_terms = get_search_terms_by_grouping(
        grouping=grouping,
        ticket_id=ticket_id,
        request_id=request_id,
        conn=conn
    )
    return Series(
        name=f"{ticket_id}: {search_terms}",
        data=data_with_proper_date_format,
        ticket_id=ticket_id
    )


def get_sql_for_grouping(grouping: Literal["day", "month", "year", "gallicaMonth", "gallicaYear"]):
    match grouping:
        case "day":
            return """

            WITH binned_frequencies AS (
                SELECT year, month, day, count(*) AS mentions 
                FROM results 
                WHERE requestid = %s
                AND ticketid = %s 
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
        case "month":
            return """

            WITH binned_frequencies AS
                (SELECT year, month, count(*) AS mentions 
                FROM results continuous
                WHERE requestid = %s
                AND ticketid = %s 
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
        case "year":
            return """

            WITH binned_frequencies AS
                (SELECT year, count(*) AS mentions 
                FROM results 
                WHERE requestid=%s
                AND ticketid = %s
                AND year IS NOT NULL
                GROUP BY year 
                ORDER BY year),

                averaged_frequencies AS
                (SELECT year, 
                        AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM binned_frequencies)

            SELECT year, avgFrequency::float8
            FROM averaged_frequencies;
            
            """
        case "gallicaYear":
            return """
            
            SELECT year, avgFrequency::float8 
            FROM (
                SELECT year, AVG(count) 
                OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM (
                    SELECT year, sum(count) as count
                    FROM groupcounts
                    WHERE requestid = %s
                    AND ticketid = %s
                    GROUP BY year
                    ORDER BY year
                ) AS counts
            ) AS avgedCounts;
            
            """
        case "gallicaMonth":
            return """
            
            SELECT year, month, avgFrequency::float8
            FROM (
                SELECT year, month, AVG(count) 
                OVER (ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM (
                    SELECT year, month, sum(count) as count
                    FROM groupcounts
                    WHERE requestid = %s
                    AND ticketid = %s
                    GROUP BY year, month
                    ORDER BY year, month
                ) AS counts
            ) AS avgedCounts;
            
            """


def get_search_terms_by_grouping(
        grouping: Literal["day", "month", "year", "gallicaMonth", "gallicaYear"],
        ticket_id: int,
        request_id: int,
        conn
):
    table = 'FROM results' if grouping in ['day', 'month', 'year'] else 'FROM groupcounts'

    get_terms = f"""
        SELECT array_agg(DISTINCT searchterm) 
        {table}
        WHERE requestid=%s 
        AND ticketid = %s;
        """

    with conn.cursor() as curs:
        curs.execute(get_terms, (
            request_id,
            ticket_id
        ))
        return curs.fetchone()[0]


def get_from_db(conn, params: Tuple, sql: str):
    with conn.cursor() as curs:
        curs.execute(
            sql,
            params
        )
        return curs.fetchall()


def get_rows_ymd_timestamp(row):
    year = row[0]
    month = row[1]
    day = row[2]
    frequency = row[3]
    date = f'{year}-{month:02d}-{day:02d}'
    return get_timestamp(date), frequency


def get_rows_ym_timestamp(row):
    year = row[0]
    month = row[1]
    frequency = row[2]
    date = f'{year}-{month:02d}-01'
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


def get_params_for_ticket_and_settings(ticketID, settings):
    if settings["continuous"] == 'true':
        return (
            settings["requestID"],
            ticketID,
            settings["startDate"],
            settings["endDate"],
            settings["averageWindow"]
        )
    elif settings["groupBy"] in ["gallicaYear", "gallicaMonth"]:
        return (
            settings["averageWindow"],
            settings["requestID"],
            ticketID
        )
    else:
        return (
            settings["requestID"],
            ticketID,
            settings["averageWindow"]
        )