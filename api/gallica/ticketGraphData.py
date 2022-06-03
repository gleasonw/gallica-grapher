import psycopg2
import json


class TicketGraphData:
    def __init__(self,
                 requestid,
                 dbconnection,
                 averagewindow=11,
                 groupby='month'):

        self.dbConnection = dbconnection
        self.requestID = requestid
        self.averageWindow = int(averagewindow)
        self.groupBy = groupby
        self.request = None
        self.searchTerms = []
        self.data = []
        self.jsonedData = ''

        self.makeGraphJSON()

    def getGraphJSON(self):
        return self.jsonedData

    def makeGraphJSON(self):
        self.buildQueryForGraphData()
        self.graphJSON = self.runQuery()

    def buildQueryForGraphData(self):
        if self.groupBy == "day":
            self.initDayRequest()
        elif self.groupBy == "month":
            self.initMonthRequest()
        else:
            self.initYearRequest()

    def initDayRequest(self):
        self.request = """
        SELECT date, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
        FROM (SELECT date, count(*) AS mentions 
            FROM results WHERE requestid = %s 
            GROUP BY date ORDER BY date ASC) AS countTable;
        """

    def initMonthRequest(self):
        self.request = """
        SELECT year || '-' || month as issuedate, AVG(mentions) 
        OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
        FROM (SELECT date_part('month', date) AS month, date_part('year', date) AS year, count(*) AS mentions 
            FROM results WHERE requestid = %s 
            GROUP BY date_part('month', date), date_part('year', date) ORDER BY year,month ASC) AS countTable;
        """

    def initYearRequest(self):
        self.request = """
        SELECT year, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
        FROM (SELECT date_part('year', date) AS year, count(*) AS mentions 
            FROM results WHERE requestid = %s
            GROUP BY date_part('year', date) ORDER BY year ASC) AS countTable;
        """

    def runQuery(self):
        self.getSearchTerms()
        self.fetchQueryResults()
        self.createJSON()

    def getSearchTerms(self):
        getSearchTerms = """
        SELECT array_agg(DISTINCT searchterm) FROM results WHERE requestid = %s;
        """
        cursor = self.dbConnection.cursor()
        cursor.execute(getSearchTerms, (self.requestID,))
        self.searchTerms = cursor.fetchone()[0]

    def fetchQueryResults(self):
        cursor = self.dbConnection.cursor()
        cursor.execute(self.request, (self.averageWindow, self.requestID,))
        self.data = cursor.fetchall()

    def createJSON(self):
        dataToJson = {
            'name': self.searchTerms,
            'data': self.data
        }
        self.jsonedData = json.dumps(dataToJson,
                                     indent=4,
                                     sort_keys=True,
                                     default=str)

if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        database="gallicagrapher",
        user="wgleason",
        password="ilike2play"
    )
    grapher = TicketGraphData("ecae3a19-2f11-4517-88cd-c86ca59bb720",
                              conn,
                              groupby='year',
                              averagewindow=0)
    json = grapher.getGraphJSON()
    print(json)
    conn.close()
