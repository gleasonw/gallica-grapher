import datetime
import ciso8601
from db import DB


# TODO: tests with continuous settings
class TicketGraphSeriesBatch:

    def __init__(self, settings):
        self.dbConnection = DB().getConn()
        self.dataBatches = []
        self.settings = settings
        self.requestIDs = settings["ticketIDs"].split(",")
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
            self.requestIDs))
        self.dbConnection.close()

    def selectOneSeries(self, requestID):
        series = TicketGraphSeries(
            requestID,
            self.settings,
            self.dbConnection)
        return [requestID, series.getSeries()]


def parseContinuous(cont):
    if cont.lower() == "true":
        return True
    else:
        return False


class TicketGraphSeries:

    def __init__(self,
                 requestid,
                 settings,
                 dbConnection):

        self.continuous = parseContinuous(settings["continuous"])
        self.requestID = requestid
        self.averageWindow = int(settings["averageWindow"])
        self.timeBin = settings["groupBy"]
        dateRange = settings["dateRange"].split(",")
        self.lowYear = dateRange[0]
        self.highYear = dateRange[1]
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
        
        WITH binned_frequencies AS (
            SELECT year, month, day, count(*) AS mentions 
            FROM results 
            WHERE requestid = %s 
                AND month IS NOT NULL
                AND day IS NOT NULL
            GROUP BY year, month, day 
            ORDER BY year, month, day),
            
            averaged_frequencies AS (
            SELECT year, month, day, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies)
            
        SELECT year, month, day, avgFrequency::numeric
            FROM averaged_frequencies;
                
        """

    def initDayContinuousPaperRequest(self):
        self.request = """
        
        WITH ticket_results AS 
            (SELECT year, month, day, paperid
            FROM results 
            WHERE requestid=%s
                AND month IS NOT NULL 
                AND day IS NOT NULL),
        
            binned_results_only_continuous AS 
            (SELECT year, month, day, count(*) AS mentions 
            FROM 
                ticket_results
                    
                JOIN papers 
                ON ticket_results.paperid = papers.code
                    AND papers.startdate < %s
                    AND papers.enddate > %s
                    AND continuous IS TRUE
                GROUP BY year, month, day 
                ORDER BY year, month, day),
                
            averaged_frequencies AS 
            (SELECT year, month, day, 
                AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_results_only_continuous)
        
        SELECT year, month, day, avgFrequency::numeric
        FROM averaged_frequencies;
        """

    def initMonthRequest(self):
        self.request = """
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
        
        SELECT year, month, avgFrequency::numeric 
        FROM averaged_frequencies;
        """

    def initMonthContinuousPaperRequest(self):
        self.request = """
        WITH ticket_results AS
            (SELECT year, month, paperid
            FROM results 
            WHERE requestid=%s
                AND month IS NOT NULL),
                
            binned_frequencies_only_continuous AS
                (SELECT year, month, count(*) AS mentions 
                FROM 
                    ticket_results

                    JOIN papers 
                    ON ticket_results.paperid = papers.code
                        AND papers.startdate < %s
                        AND papers.enddate > %s
                        AND continuous IS TRUE
                GROUP BY year, month
                ORDER BY year, month),
                
            averaged_frequencies AS
                (SELECT year, month, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM binned_frequencies_only_continuous)
                
        SELECT year, month, avgFrequency::numeric
        FROM averaged_frequencies;
        """

    def initYearRequest(self):
        self.request = """
        WITH binned_frequencies AS
            (SELECT year, count(*) AS mentions 
            FROM results 
            WHERE requestid = %s
                AND year IS NOT NULL
            GROUP BY year 
            ORDER BY year),
            
            averaged_frequencies AS
            (SELECT year, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies)
            
        SELECT year, avgFrequency::numeric
        FROM averaged_frequencies;
        """

    def initYearContinuousPaperRequest(self):
        self.request = """
        WITH ticket_results AS
            (SELECT year, paperid
            FROM results 
            WHERE requestid=%s),
            
            binned_frequencies_only_continuous AS
            (SELECT year, count(*) AS mentions 
            FROM 
                ticket_results

                JOIN papers 
                ON ticket_results.paperid = papers.code
                    AND papers.startdate < %s
                    AND papers.enddate > %s
                    AND continuous IS TRUE
                GROUP BY year
                ORDER BY year),
                
            averaged_frequencies AS
            (SELECT year,
                AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies_only_continuous)
                
        SELECT year, avgFrequency::numeric
        FROM averaged_frequencies;
        """

    def runQuery(self):
        self.getSearchTerms()
        self.executeQuery()

    def getSearchTerms(self):
        getSearchTerms = """
        SELECT array_agg(DISTINCT searchterm) FROM results WHERE requestid = %s;
        """
        cursor = self.dbConnection.cursor()
        cursor.execute(getSearchTerms, (self.requestID,))
        self.searchTerms = cursor.fetchone()[0]

    def executeQuery(self):
        with self.dbConnection.cursor() as curs:
            if self.continuous:
                params = (
                    self.requestID,
                    self.averageWindow,
                    self.lowYear,
                    self.highYear,
                )
            else:
                params = (
                    self.requestID,
                    self.averageWindow,
                )
            curs.execute(
                self.request,
                params
            )
            self.data = curs.fetchall()
