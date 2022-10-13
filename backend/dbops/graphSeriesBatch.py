from utils.psqlconn import PSQLconn
import datetime
import ciso8601


class GraphSeriesBatch:

    def __init__(self):
        self.dbConnection = PSQLconn().getConn()

    def getSeriesForSettings(self, settings):
        if not self.dbConnection:
            self.dbConnection = PSQLconn().getConn()
        ticketIDs = settings['ticketIDs'].split(',')
        dataBatches = list(map(
            lambda ticketID: self.selectOneSeries(
                ticketID=ticketID,
                settings=settings,
            ),
            ticketIDs
        ))
        return {
            dataBatch.getRequestID(): dataBatch.getSeries()
            for dataBatch in dataBatches
        }

    def selectOneSeries(self, ticketID, settings):
        return TicketGraphSeries(
            ticketID=ticketID,
            settings=settings,
            dbConnection=self.dbConnection
        )


class TicketGraphSeries:

    def __init__(self, ticketID, settings, dbConnection):
        self.ticketID = ticketID
        self.requestID = settings["requestID"]
        self.dbConnection = dbConnection
        self.series = self.getHighchartsFormattedDataForSettings(settings)

    def getRequestID(self):
        return self.requestID

    def getSeries(self):
        return {
            'name': self.searchTerms,
            'data': self.data
        }

    def getHighchartsFormattedDataForSettings(self, settings):
        timeBin = settings["groupBy"]
        sql = self.getSQLforSettings()
        if timeBin == "day" or timeBin == "month":
            self.calculateJStime()
        elif timeBin == "year":
            self.data = self.dataNoJSTimestamp
        else:
            raise Exception("Invalid time bin")
        return {
            'name': self.getSearchTermsForTicket(),
            'data': self.getFromDBForSettings(settings)
        }

    #TODO: rewrite with dictionary routing
    def getSQLforSettings(self):
        if self.timeBin == "day" and self.continuous:
            return self.initDayContinuousPaperRequest()
        elif self.timeBin == "day" and not self.continuous:
            return self.initDayRequest()
        elif self.timeBin == "month" and self.continuous:
            return self.initMonthContinuousPaperRequest()
        elif self.timeBin == "month" and not self.continuous:
            return self.initMonthRequest()
        elif self.timeBin == "year" and self.continuous:
            return self.initYearContinuousPaperRequest()
        elif self.timeBin == "year" and not self.continuous:
            return self.initYearRequest()
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
            (SELECT year, month, day, papercode
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
                ON ticket_results.papercode = papers.code
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
            (SELECT year, month, papercode
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND month IS NOT NULL),
                
            binned_frequencies_only_continuous AS
                (SELECT year, month, count(*) AS mentions 
                FROM 
                    ticket_results

                    JOIN papers 
                    ON ticket_results.papercode = papers.code
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
            (SELECT year, papercode
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND year IS NOT NULL),
            
            binned_frequencies_only_continuous AS
            (SELECT year, count(*) AS mentions 
            FROM 
                ticket_results

                JOIN papers 
                ON ticket_results.papercode = papers.code
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

    def getSearchTerms(self):
        getSearchTerms = """
        SELECT array_agg(DISTINCT searchterm) 
        FROM results 
        WHERE requestid=%s 
        AND ticketid = %s;
        """
        cursor = self.dbConnection.cursor()
        cursor.execute(getSearchTerms, (self.requestID, self.ticketID,))
        return cursor.fetchone()[0]

    def getFromDBForSettings(self, settings):
        continuous = settings["continuous"].lower() == "true"
        lowYear = settings["lowYear"]
        highYear = settings["highYear"]
        averageWindow = settings["averageWindow"]
        with self.dbConnection.cursor() as curs:
            if continuous:
                params = (
                    self.requestID,
                    self.ticketID,
                    lowYear,
                    highYear,
                    averageWindow
                )
            else:
                params = (
                    self.requestID,
                    self.ticketID,
                    averageWindow,
                )
            curs.execute(
                self.request,
                params
            )
            return curs.fetchall()

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
            try:
                dateObject = ciso8601.parse_datetime(date)
                dateObject = dateObject.replace(tzinfo=datetime.timezone.utc)
                timestamp = datetime.datetime.timestamp(dateObject) * 1000
            except ValueError:
                print(f"erred with date: {date}")
                return None
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
