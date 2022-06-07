import psycopg2
import json


class TicketGraphData:
    def __init__(self,
                 requestid,
                 averagewindow=11,
                 groupby='month'):

        self.dbConnection = None
        self.requestID = requestid
        self.averageWindow = int(averagewindow)
        self.groupBy = groupby
        self.request = None
        self.searchTerms = []
        self.data = []
        self.jsonedData = ''

        self.initDBConnection()
        self.makeGraphJSON()

    def getGraphJSON(self):
        return self.jsonedData

    def makeGraphJSON(self):
        self.buildQueryForGraphData()
        self.runQuery()

    def buildQueryForGraphData(self):
        if self.groupBy == "day":
            self.initDayRequest()
        elif self.groupBy == "month":
            self.initMonthRequest()
        else:
            self.initYearRequest()

    def initDayRequest(self):
        self.request = """
        SELECT year || '-' || month || '-' || day as issuedate, AVG(mentions)
        OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
        FROM (SELECT year, month, day, count(*) AS mentions 
            FROM results WHERE requestid = %s 
            AND month IS NOT NULL
            AND day IS NOT NULL
            GROUP BY year, month, day 
            ORDER BY year, month, day) AS countTable;
        """

    def initMonthRequest(self):
        self.request = """
        SELECT year || '-' || month as issuedate, AVG(mentions) 
        OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
        FROM (SELECT year, month, count(*) AS mentions 
            FROM results WHERE requestid = %s 
            AND month IS NOT NULL
            GROUP BY year, month
            ORDER BY year,month) AS countTable;
        """

    def initYearRequest(self):
        self.request = """
        SELECT year as issuedate, AVG(mentions) 
        OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
        FROM (SELECT year, count(*) AS mentions 
            FROM results WHERE requestid = %s
            GROUP BY year 
            ORDER BY year) AS countTable;
        """

    def runQuery(self):
        self.getSearchTerms()
        self.binRecordsAndFetch()
        self.floatDecimals()
        self.createJSON()

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

    def floatDecimals(self):
        pass

    def createJSON(self):
        dataToJson = {
            'name': self.searchTerms,
            'data': self.data
        }
        self.jsonedData = json.dumps(dataToJson,
                                     indent=4,
                                     sort_keys=True)

    def initDBConnection(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        self.dbConnection = conn
