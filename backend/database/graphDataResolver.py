from database.sqlForGraph import (
    get_sql_for_settings,
    get_params_for_ticket_and_settings
)
import datetime
import ciso8601


def get_series_for_tickets(settings, conn):
    ticket_ids = settings['ticketIDs'].split(',')
    data_batches = list(map(
        lambda ticket_id: HighchartsSeriesForTicket(
            ticketID=ticket_id,
            settings=settings,
            conn=conn
        ),
        ticket_ids
    ))
    return {
        dataBatch.get_ticket_id(): dataBatch.get()
        for dataBatch in data_batches
    }


class HighchartsSeriesForTicket:

    def __init__(self, ticketID, settings, conn):
        self.conn = conn
        self.ticketID = ticketID
        self.requestID = settings["requestID"]
        self.series = self.build_highcharts_series(settings)

    def get_ticket_id(self):
        return self.ticketID

    def get(self):
        return self.series

    def build_highcharts_series(self, settings):
        data = self.get_from_db(
            params=get_params_for_ticket_and_settings(
                ticketID=self.ticketID,
                settings=settings
            ),
            sql=get_sql_for_settings(
                timeBin=settings["groupBy"],
                continuous=settings["continuous"],
            )
        )
        data_with_proper_date_format = self.transform_date_for_settings(data, settings)
        return {
            'name': f"{self.ticketID}: {self.get_search_terms_by_grouping(settings['groupBy'])}",
            'data': data_with_proper_date_format,
        }

    def get_search_terms_by_grouping(self, grouping):

        table = 'FROM results' if grouping in ['day', 'month', 'year'] else 'FROM groupcounts'

        get_terms = f"""
        SELECT array_agg(DISTINCT searchterm) 
        {table}
        WHERE requestid=%s 
        AND ticketid = %s;
        """

        with self.conn.cursor() as curs:
            curs.execute(get_terms, (
                self.requestID,
                self.ticketID
            ))
            return curs.fetchone()[0]

    def get_from_db(self, params, sql):
        with self.conn.cursor() as curs:
            curs.execute(
                sql,
                params
            )
            return curs.fetchall()

    def transform_date_for_settings(self, data, settings):
        if settings["groupBy"] == "day":
            return list(map(self.getRowsWithYMDtimestamp, data))
        elif settings["groupBy"] == "month" or settings["groupBy"] == "gallicaMonth":
            return list(map(self.getRowsWithYearMonthTimestamp, data))
        else:
            return data

    def getRowsWithYMDtimestamp(self, row):
        year = row[0]
        month = row[1]
        day = row[2]
        frequency = row[3]
        date = f'{year}-{month:02d}-{day:02d}'
        return self.dateToTimestamp(date), frequency

    def getRowsWithYearMonthTimestamp(self, row):
        year = row[0]
        month = row[1]
        frequency = row[2]
        date = f'{year}-{month:02d}-01'
        return self.dateToTimestamp(date), frequency

    def dateToTimestamp(self, date):
        try:
            dateObject = ciso8601.parse_datetime(date)
            dateObject = dateObject.replace(tzinfo=datetime.timezone.utc)
            timestamp = datetime.datetime.timestamp(dateObject) * 1000
        except ValueError:
            print(f"erred with date: {date}")
            return None
        return timestamp
