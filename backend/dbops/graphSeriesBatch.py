from dbops.sqlForGraph import SQLforGraph
import datetime
import ciso8601
from dbops.connContext import getConn


class GraphSeriesBatch:

    def __init__(self):
        self.sqlGetter = SQLforGraph()

    def getSeriesForSettings(self, settings):
        ticketIDs = settings['ticketIDs'].split(',')
        dataBatches = list(map(
            lambda ticketID: self.selectOneSeries(
                ticketID=ticketID,
                settings=settings,
            ),
            ticketIDs
        ))
        return {
            dataBatch.getTicketID(): dataBatch.getSeries()
            for dataBatch in dataBatches
        }

    def selectOneSeries(self, ticketID, settings):
        return HighchartsSeriesForTicket(
            ticketID=ticketID,
            settings=settings,
            sqlGetter=self.sqlGetter,
        )


class HighchartsSeriesForTicket:

    def __init__(self, ticketID, settings, sqlGetter):
        self.ticketID = ticketID
        self.requestID = settings["requestID"]
        self.sqlGetter = sqlGetter
        self.series = self.buildHighchartsSeries(settings)

    def getTicketID(self):
        return self.ticketID

    def getSeries(self):
        return self.series

    def buildHighchartsSeries(self, settings):
        data = self.getFromDB(
            params=self.sqlGetter.getParamsForTicketWithSettings(
                ticketID=self.ticketID,
                settings=settings
            ),
            sql=self.sqlGetter.getSQLforSettings(
                timeBin=settings["groupBy"],
                continuous=settings["continuous"],
            )
        )
        dataWithProperDateFormat = self.transformDateForSettings(data, settings)
        return {
            'name': f"{self.ticketID}: {self.getSearchTermsByGrouping(settings['groupBy'])}",
            'data': dataWithProperDateFormat,
        }

    def getSearchTermsByGrouping(self, grouping):
        dbSource = 'FROM results' if grouping in ['day', 'month', 'year'] else 'FROM groupcounts'
        getSearchTerms = f"""
        SELECT array_agg(DISTINCT searchterm) 
        {dbSource}
        WHERE requestid=%s 
        AND ticketid = %s;
        """
        conn = getConn()
        with conn.cursor() as curs:
            curs.execute(getSearchTerms, (
                self.requestID,
                self.ticketID
            ))
            return curs.fetchone()[0]

    def getFromDB(self, params, sql):
        conn = getConn()
        with conn.cursor() as curs:
            curs.execute(
                sql,
                params
            )
            return curs.fetchall()

    def transformDateForSettings(self, data, settings):
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
