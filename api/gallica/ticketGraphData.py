import psycopg2
import json
import time
import ciso8601


class TicketGraphData:
    def __init__(self,
                 requestID,
                 connectionToDB,
                 averageWindow=11,
                 groupBy='month'):

        self.dbConnection = connectionToDB
        self.requestID = requestID
        self.pandasDataFrame = None
        self.averageWindow = int(averageWindow)
        self.groupBy = groupBy
        self.graphJSON = None
        self.request = None
        self.searchTerms = []

        self.makeGraphJSON()

    def getGraphJSON(self):
        return self.graphJSON

    def makeGraphJSON(self):
        self.buildQueryForGraphData()
        self.graphJSON = self.executeQuery()

    def buildQueryForGraphData(self):
        if self.groupBy == "day":
            self.request = """
            SELECT issuedate, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date as issuedate, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                GROUP BY date ORDER BY date ASC) AS countTable;
            """
        elif self.groupBy == "month":
            self.request = """
            SELECT make_date(year::integer, month::integer, 1) as issuedate, AVG(mentions) 
            OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('month', date) AS month, date_part('year', date) AS year, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                GROUP BY date_part('month', date), date_part('year', date) ORDER BY year,month ASC) AS countTable;
            """
        else:
            self.request = """
            SELECT issuedate, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('year', date) AS issuedate, count(*) AS mentions 
                FROM results WHERE requestid = %s
                GROUP BY date_part('year', date) ORDER BY issuedate ASC) AS countTable;
            """

    def executeQuery(self):
        self.getSearchTerms()
        data = self.fetchQueryResults()
        data = self.makeDateFrequencyPairIntoList(data)
        dataToJson = {
            'name': self.searchTerms,
            'data': data
        }
        jsonedData = json.dumps(dataToJson)
        return [jsonedData]

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
        data = cursor.fetchall()
        return data

    @staticmethod
    def makeDateFrequencyPairIntoList(data):
        for i, entry in enumerate(data):
            if isinstance(entry, str):
                entry = entry.split(', ')
                date = ciso8601.parse_datetime(entry[0])
            else:
                date = entry[0]
            dateInMilliSeconds = time.mktime(date.timetuple()) * 1000
            frequency = float(entry[1])
            data[i] = [dateInMilliSeconds, frequency]
        return data


if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="wglea",
        password="ilike2play"
    )
    grapher = TicketGraphData("9f036013-3c68-4bd2-ab02-4dd022171d5f", conn, averageWindow=11)
    grapher.makeGraphJSON()
    conn.close()
