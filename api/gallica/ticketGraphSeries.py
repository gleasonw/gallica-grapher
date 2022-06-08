
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
            'data': self.data,
            'keywords': self.searchTerms
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