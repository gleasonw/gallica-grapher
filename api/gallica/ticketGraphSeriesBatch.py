import datetime
import ciso8601
from db import DB


class TicketGraphSeriesBatch:
    def __init__(self,
                 requestids,
                 averagewindow=0,
                 groupby='day'):

        self.dbConnection = DB().getConn()
        self.dataBatches = []

        if requestids and groupby:
            self.averageWindow = int(averagewindow)
            self.requestIDs = requestids.split(',')
            self.groupBy = groupby
            self.selectGraphSeries()

    def getSeries(self):
        return self.dataBatches

    def selectGraphSeries(self):
        self.dataBatches = list(map(
            self.selectDataForRequestID,
            self.requestIDs))
        self.dbConnection.close()

    def selectDataForRequestID(self, requestID):
        series = TicketGraphSeries(
            requestID,
            self.dbConnection,
            self.averageWindow,
            self.groupBy)
        return {requestID: series.getSeries()}


class TicketGraphSeries:

    def __init__(self,
                 requestid,
                 dbConnection,
                 averagewindow=0,
                 groupby='month'):

        self.requestID = requestid
        self.averageWindow = int(averagewindow)
        self.timeBin = groupby
        self.data = []
        self.searchTerms = []
        self.request = None

        self.dbConnection = dbConnection
        self.makeSeries()

    def getSeries(self):
        return {
            'name': self.searchTerms,
            'data': self.data
        }

    def makeSeries(self):
        self.buildQueryForGraphData()
        self.runQuery()

    def buildQueryForGraphData(self):
        if self.timeBin == "day":
            self.initDayRequest()
        elif self.timeBin == "month":
            self.initMonthRequest()
        else:
            self.initYearRequest()

    def initDayRequest(self):
        self.request = """
        SELECT year, month, day, avgFrequency::float8
            FROM (SELECT year, month, day, AVG(mentions)
            OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT year, month, day, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                AND month IS NOT NULL
                AND day IS NOT NULL
                GROUP BY year, month, day 
                ORDER BY year, month, day) 
                AS countTable) AS decimalAvg;
        """

    def initMonthRequest(self):
        self.request = """
        SELECT year, month, avgFrequency::float8 
            FROM (SELECT year, month, AVG(mentions) 
            OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT year, month, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                AND month IS NOT NULL
                GROUP BY year, month
                ORDER BY year,month) AS countTable) AS decimalAvg;
        """

    def initYearRequest(self):
        self.request = """
        SELECT year, avgFrequency::float8 
            FROM(SELECT year, AVG(mentions)
            OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT year, count(*) AS mentions 
                FROM results WHERE requestid = %s
                AND year IS NOT NULL
                GROUP BY year 
                ORDER BY year) AS countTable) AS decimalAvg;
        """

    def runQuery(self):
        self.getSearchTerms()
        self.binRecordsAndFetch()
        self.parseDatesToJSTimestamp()

    def getSearchTerms(self):
        getSearchTerms = """
        SELECT array_agg(DISTINCT searchterm) FROM results WHERE requestid = %s;
        """
        cursor = self.dbConnection.cursor()
        cursor.execute(getSearchTerms, (self.requestID,))
        self.searchTerms = cursor.fetchone()[0]

    def binRecordsAndFetch(self):
        with self.dbConnection.cursor() as curs:
            curs.execute(self.request, (self.averageWindow, self.requestID,))
            self.data = curs.fetchall()

    def parseDatesToJSTimestamp(self):

        def makeMonthTwoDigits(month):
            if month < 10:
                month = f'0{month}'
            return month

        def makeDayTwoDigits(day):
            if day < 10:
                day = f'0{day}'
            return day

        def dateToTimestamp(date):
            dateObject = ciso8601.parse_datetime(date)
            timestamp = datetime.datetime.timestamp(dateObject) * 1000
            return timestamp

        # Dummy day added to simplify Highcharts comparison.
        def parseYearMonRecord(record):
            year = record[0]
            month = makeMonthTwoDigits(record[1])
            freq = record[2]
            JStimestamp = dateToTimestamp(f"{year}-{month}-01")
            return [
                JStimestamp,
                freq
            ]

        def parseYearMonDayRecord(record):
            year = record[0]
            month = makeMonthTwoDigits(record[1])
            day = makeDayTwoDigits(record[2])
            freq = record[3]
            JStimestamp = dateToTimestamp(f"{year}-{month}-{day}")
            return [
                JStimestamp,
                freq
            ]

        if self.timeBin == 'year':
            dataWithTimestamps = self.data
        elif self.timeBin == 'month':
            dataWithTimestamps = list(map(
                parseYearMonRecord,
                self.data
            ))
        else:
            dataWithTimestamps = list(map(
                parseYearMonDayRecord,
                self.data
            ))
        self.data = dataWithTimestamps
