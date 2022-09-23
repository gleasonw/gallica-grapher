from utils.psqlconn import PSQLconn
import datetime
import ciso8601


class GraphSeriesBatch:

    def __init__(self, settings):
        self.dbConnection = PSQLconn().getConn()
        self.dataBatches = []
        self.settings = settings
        self.ticketIDs = settings["ticketIDs"].split(",")
        self.requestID = settings["requestID"]

        self.selectAllSeriesFromDB()

    def getSeriesBatch(self):
        dataBatchesDict = {}
        for dataBatch in self.dataBatches:
            requestID = dataBatch[0]
            series = dataBatch[1]
            dataBatchesDict[requestID] = series
        return dataBatchesDict

    def selectAllSeriesFromDB(self):
        self.dataBatches = list(map(
            self.selectOneSeries,
            self.ticketIDs))
        self.dbConnection.close()

    def selectOneSeries(self, ticketID):
        series = TicketGraphSeries(
            self.requestID,
            ticketID,
            self.settings,
            self.dbConnection)
        return [ticketID, series.getSeries()]


class TicketGraphSeries:

    def __init__(self,
                 requestID,
                 ticketid,
                 settings,
                 dbConnection):

        self.continuous = settings["continuous"].lower() == "true"
        self.ticketid = ticketid
        self.requestID = requestID
        self.averageWindow = int(settings["averageWindow"])
        self.timeBin = settings["groupBy"]
        dateRange = settings["dateRange"].split(",")
        self.lowYear = dateRange[0]
        self.highYear = dateRange[1]
        self.dataNoJSTimestamp = []
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
        self.buildQueryForSeries()
        self.runQuery()
        if self.timeBin == "day" or self.timeBin == "month":
            self.calculateJStime()
        elif self.timeBin == "year":
            self.data = self.dataNoJSTimestamp
        else:
            raise Exception("Invalid time bin")

    #TODO: rewrite with dictionary routing
    def buildQueryForSeries(self):
        if self.timeBin == "day" and self.continuous:
            self.initDayContinuousPaperRequest()
        elif self.timeBin == "day" and not self.continuous:
            self.initDayRequest()
        elif self.timeBin == "month" and self.continuous:
            self.initMonthContinuousPaperRequest()
        elif self.timeBin == "month" and not self.continuous:
            self.initMonthRequest()
        elif self.timeBin == "year" and self.continuous:
            self.initYearContinuousPaperRequest()
        elif self.timeBin == "year" and not self.continuous:
            self.initYearRequest()
        else:
            raise Exception("Invalid time bin")

    def initDayRequest(self):
        self.request = """
        
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
            SELECT year, month, day, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies)
            
        SELECT year, month, day, avgFrequency::float8
            FROM averaged_frequencies;
                
        """

    def initDayContinuousPaperRequest(self):
        self.request = """
        
        WITH ticket_results AS 
            (SELECT year, month, day, paperid
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND month IS NOT NULL 
            AND day IS NOT NULL),
        
            binned_results_only_continuous AS 
            (SELECT year, month, day, count(*) AS mentions 
            FROM 
                ticket_results
                    
                JOIN papers 
                ON ticket_results.paperid = papers.code
                    AND papers.startdate <= %s
                    AND papers.enddate >= %s
                    AND continuous IS TRUE
                GROUP BY year, month, day 
                ORDER BY year, month, day),
                
            averaged_frequencies AS 
            (SELECT year, month, day, 
                AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_results_only_continuous)
        
        SELECT year, month, day, avgFrequency::float8
        FROM averaged_frequencies;
        """

    def initMonthRequest(self):
        self.request = """
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

    def initMonthContinuousPaperRequest(self):
        self.request = """
        WITH ticket_results AS
            (SELECT year, month, paperid
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND month IS NOT NULL),
                
            binned_frequencies_only_continuous AS
                (SELECT year, month, count(*) AS mentions 
                FROM 
                    ticket_results

                    JOIN papers 
                    ON ticket_results.paperid = papers.code
                        AND papers.startdate <= %s
                        AND papers.enddate >= %s
                        AND continuous IS TRUE
                GROUP BY year, month
                ORDER BY year, month),
                
            averaged_frequencies AS
                (SELECT year, month, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM binned_frequencies_only_continuous)
                
        SELECT year, month, avgFrequency::float8
        FROM averaged_frequencies;
        """

    def initYearRequest(self):
        self.request = """
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

    def initYearContinuousPaperRequest(self):
        self.request = """
        WITH ticket_results AS
            (SELECT year, paperid
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND year IS NOT NULL),
            
            binned_frequencies_only_continuous AS
            (SELECT year, count(*) AS mentions 
            FROM 
                ticket_results

                JOIN papers 
                ON ticket_results.paperid = papers.code
                    AND papers.startdate <= %s
                    AND papers.enddate >= %s
                    AND continuous IS TRUE
                GROUP BY year
                ORDER BY year),
                
            averaged_frequencies AS
            (SELECT year,
                AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies_only_continuous)
                
        SELECT year, avgFrequency::float8
        FROM averaged_frequencies;
        """

    def runQuery(self):
        self.getSearchTerms()
        self.executeQuery()

    def getSearchTerms(self):
        getSearchTerms = """
        SELECT array_agg(DISTINCT searchterm) FROM results WHERE ticketid = %s;
        """
        cursor = self.dbConnection.cursor()
        cursor.execute(getSearchTerms, (self.ticketid,))
        self.searchTerms = cursor.fetchone()[0]

    def executeQuery(self):
        with self.dbConnection.cursor() as curs:
            if self.continuous:
                params = (
                    self.requestID,
                    self.ticketid,
                    self.lowYear,
                    self.highYear,
                    self.averageWindow
                )
            else:
                params = (
                    self.requestID,
                    self.ticketid,
                    self.averageWindow,
                )
            curs.execute(
                self.request,
                params
            )
            self.dataNoJSTimestamp = curs.fetchall()

    def calculateJStime(self):

        def getMonthTwoDigits(month):
            if month < 10:
                return f'0{month}'
            else:
                return month

        def getDayTwoDigits(day):
            if day < 10:
                return f'0{day}'
            else:
                return day

        def dateToTimestamp(date):
            dateObject = ciso8601.parse_datetime(date)
            dateObject = dateObject.replace(tzinfo=datetime.timezone.utc)
            timestamp = datetime.datetime.timestamp(dateObject) * 1000
            return timestamp

        if self.timeBin == "day":
            for row in self.dataNoJSTimestamp:
                year = row[0]
                month = getMonthTwoDigits(row[1])
                day = getDayTwoDigits(row[2])
                frequency = row[3]
                date = f'{year}-{month}-{day}'
                self.data.append(
                    (dateToTimestamp(date), frequency)
                )
        elif self.timeBin == "month":
            for row in self.dataNoJSTimestamp:
                year = row[0]
                month = getMonthTwoDigits(row[1])
                frequency = row[2]
                date = f'{year}-{month}-01'
                self.data.append(
                    (dateToTimestamp(date), frequency)
                )
