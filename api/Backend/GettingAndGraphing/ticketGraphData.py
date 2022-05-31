import psycopg2
import json
import time
import ciso8601


class TicketGraphData:
    def __init__(self, requestID, connectionToDB, averageWindow=11, splitPapers=False, splitTerms=False,
                 groupBy='month'):
        self.dbConnection = connectionToDB
        self.requestID = requestID
        self.pandasDataFrame = None
        self.averageWindow = int(averageWindow)
        self.splitPapers = splitPapers
        self.splitTerms = splitTerms
        self.groupBy = groupBy
        self.graphJSON = None
        self.request = None

    def getGraphJSON(self):
        return self.graphJSON

    def makeGraphJSON(self):
        try:
            if self.splitPapers and not self.splitTerms:
                self.graphJSON = self.doPaperSplitQuery()
            elif self.splitPapers and self.splitTerms:
                self.graphJSON = self.doPaperSplitTermSplitQuery()
            elif not self.splitPapers and self.splitTerms:
                self.graphJSON = self.doTermSplitQuery()
            else:
                self.graphJSON = self.doBasicQuery()
        except psycopg2.DatabaseError as e:
            print(e)
        finally:
            pass

    def doPaperSplitTermSplitQuery(self):
        if self.groupBy == "day":
            self.request = """
            SELECT issuedate, (searchterm, papername) as seriesname, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date as issuedate, searchterm, papername, count(*) AS mentions 
                FROM results INNER JOIN papers ON paperid = papercode WHERE requestid = %s 
                GROUP BY date, searchterm, papername ORDER BY date ASC) AS countTable
            """
        elif self.groupBy == "month":
            self.request = """
            SELECT make_date(year::integer, month::integer, 1), (searchterm, papername) as seriesname, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('month', date) AS month, date_part('year', date) AS year, searchterm, papername, count(*) AS mentions 
                FROM results INNER JOIN papers ON paperid = papercode WHERE requestid = %s 
                GROUP BY date_part('month', date), date_part('year', date), searchterm, papername ORDER BY year,month ASC) AS countTable
            """
        elif self.groupBy == "year":
            self.request = """
            SELECT issuedate, (searchterm, papername) as seriesname, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('year', date) AS issuedate, searchterm, papername, count(*) AS mentions 
                FROM results INNER JOIN papers ON paperid = papercode WHERE requestid = %s 
                GROUP BY date_part('year', date), searchterm, papername ORDER BY year ASC) as countTable
            """
        else:
            pass
        self.request = f"""
        SELECT seriesname, array_agg(issuedate || ', ' || avgFrequency ORDER BY issuedate)
            FROM ({self.request}) AS groupedCountTable GROUP BY seriesname;
        """
        return self.fetchQueryResults()

    def doTermSplitQuery(self):
        if self.groupBy == "day":
            self.request = """
            SELECT issuedate, searchterm, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date as issuedate, searchterm, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                GROUP BY date, searchterm ORDER BY date ASC) AS countTable
            """
        elif self.groupBy == "month":
            self.request = """
            SELECT make_date(year::integer, month::integer, 1) as issuedate, searchterm, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('month', date) AS month, date_part('year', date) AS year, searchterm, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                GROUP BY date_part('month', date), date_part('year', date), searchterm ORDER BY year,month ASC) AS countTable
            """
        elif self.groupBy == "year":
            self.request = """
            SELECT issuedate, searchterm, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('year', date) AS issuedate, searchterm, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                GROUP BY date_part('year', date), searchterm ORDER BY year ASC) AS countTable
            """
        else:
            pass
        self.request = f"""
        SELECT searchterm, array_agg(issuedate || ', ' || avgFrequency ORDER BY issuedate)
            FROM ({self.request}) AS groupedCountTable GROUP BY searchterm;
        """
        return self.fetchQueryResults()

    def doPaperSplitQuery(self):
        if self.groupBy == "day":
            self.request = """
            SELECT issuedate, papername, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
             FROM (SELECT date as issuedate, papername, count(*) AS mentions
                FROM results INNER JOIN papers ON paperid = papercode WHERE requestid = %s 
                GROUP BY date, papername ORDER BY date ASC) as countTable
            """
        elif self.groupBy == "month":
            self.request = """
            SELECT make_date(year::integer, month::integer, 1) as issuedate, papername, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('month', date) AS month, date_part('year', date) AS year, papername, count(*) AS mentions
                FROM results INNER JOIN papers ON paperid = papercode WHERE requestid = %s 
                GROUP BY date_part('month', date), date_part('year', date), papername ORDER BY year,month ASC) as countTable
            """
        elif self.groupBy == "year":
            self.request = """
            SELECT issuedate, papername, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('year', date) AS issuedate, papername, count(*) AS mentions
                    FROM results INNER JOIN papers ON paperid = papercode WHERE requestid = %s 
                    GROUP BY date_part('year', date), papername ORDER BY year ASC) as countTable
            """
        else:
            pass
        self.request = f"""
        SELECT papername, array_agg(issuedate || ', ' || avgFrequency ORDER BY issuedate ASC)
            FROM ({self.request}) AS groupedCountTable GROUP BY papername;
        """
        data = self.fetchQueryResults()
        return self.addNameTag(data)

    def doBasicQuery(self):
        if self.groupBy == "day":
            self.request = """
            SELECT issuedate, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date as issuedate, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                GROUP BY date ORDER BY date ASC) AS countTable;
            """
        elif self.groupBy == "month":
            self.request = """
            SELECT make_date(year::integer, month::integer, 1) as issuedate, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('month', date) AS month, date_part('year', date) AS year, count(*) AS mentions 
                FROM results WHERE requestid = %s 
                GROUP BY date_part('month', date), date_part('year', date) ORDER BY year,month ASC) AS countTable;
            """
        elif self.groupBy == "year":
            self.request = """
            SELECT issuedate, AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (SELECT date_part('year', date) AS issuedate, count(*) AS mentions 
                FROM results WHERE requestid = %s
                GROUP BY date_part('year', date) ORDER BY issuedate ASC) AS countTable;
            """
        else:
            pass
        getSearchTerms = """
        SELECT array_agg(DISTINCT searchterm) FROM results WHERE requestid = %s;
        """
        cursor = self.dbConnection.cursor()
        cursor.execute(getSearchTerms, (self.requestID,))
        searchTerms = cursor.fetchone()[0]
        data = self.fetchQueryResults()
        data = self.makeDateFrequencyPairIntoList(data)
        dataToJson = {
            'name': searchTerms,
            'data': data
        }
        jsonedData = json.dumps(dataToJson)
        return [jsonedData]

    def fetchQueryResults(self):
        cursor = self.dbConnection.cursor()
        cursor.execute(self.request, (self.averageWindow, self.requestID,))
        data = cursor.fetchall()
        return data

    def addNameTag(self, data):
        seriesList = []
        namedDict = {}
        for nameDataPair in data:
            name = nameDataPair[0]
            data = nameDataPair[1]
            data = self.makeDateFrequencyPairIntoList(data)
            namedDict["name"] = name
            namedDict["data"] = data
            jsonedData = json.dumps(namedDict)
            seriesList.append(jsonedData)
        return seriesList

    def makeDateFrequencyPairIntoList(self, data):
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
    grapher = TicketGraphData("9f036013-3c68-4bd2-ab02-4dd022171d5f", conn, splitPapers=True, averageWindow=11)
    grapher.makeGraphJSON()
    conn.close()
