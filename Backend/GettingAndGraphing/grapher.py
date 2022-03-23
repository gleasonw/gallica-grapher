import json
from os.path import dirname

import pandas
import shutil
import os

import seaborn as sb
import matplotlib.pyplot as plt
import psycopg2

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class Grapher:
    def __init__(self, graphSettings, requestID):
        self.requestID = requestID
        conn = None
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="wglea",
                password="ilike2play"
            )
            cursor = conn.cursor()
            self.tenMostPapers = self.fetchTenMostPapers(cursor)
            self.pandasDataFrame = self.createPandasDataFrameFromDB(cursor)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            raise
        finally:
            if conn is not None:
                conn.close()
        self.settings = graphSettings
        self.directory = os.path.dirname(os.path.abspath(__file__))

    def fetchTenMostPapers(self, psqlCursor):
        sql = """
            SELECT papername, count, position FROM toppapers WHERE requestid = %s;
        """
        psqlCursor.execute(sql, (self.requestID,))
        return psqlCursor.fetchall()

    def fetchQueryResults(self, psqlCursor):
        sql = """
            SELECT searchterm, month, year, papers.papername FROM results INNER JOIN papers ON paperid = papercode WHERE requestid = %s;
        """
        psqlCursor.execute(sql, (self.requestID,))
        return psqlCursor.fetchall()

    def createPandasDataFrameFromDB(self, psqlCursor):
        data = self.fetchQueryResults(psqlCursor)
        dataFrame = pandas.DataFrame(data, columns=["term", "month", "year", "newspaper"])
        return dataFrame

    def graph(self):
        self.parseGraphSettings()

    def parseGraphSettings(self):
        if self.settings["graphType"] == "bar":
            self.makeBarGraph(window=6)
        else:
            pass

    def makeBarGraph(self, **kwargs):
        averageWindow = kwargs["window"]
        monYearDF = self.pandasDataFrame.groupby([self.pandasDataFrame["year"],self.pandasDataFrame["month"]]).agg('count')[["term"]]
        monYearDF = monYearDF.rename(columns={"term":"mentions"})
        monYearDF.index = pandas.to_datetime(monYearDF.index, format="(%Y, %m)")
        monYearDF['movAvg'] = monYearDF['mentions'].rolling(window=averageWindow).mean()
        fig = sb.relplot(
            data=monYearDF,
            x=monYearDF.index,
            y='movAvg',
            kind='line')
        fig.figure.autofmt_xdate()
        filename = "{id}.svg".format(id=self.requestID)
        plt.xlabel("Date")
        plt.ylabel("Keyword Mention Frequency ({window} month rolling)".format(window=averageWindow))
        plt.savefig(filename, dpi=300)
        pathToStaticFolder = dirname(dirname(dirname(os.path.realpath(__file__))))
        pathToStaticFolder = os.path.join(pathToStaticFolder, 'Frontend/static')
        shutil.move(filename, os.path.join(pathToStaticFolder, filename))


if __name__ == "__main__":
    settings = {'graphType':'bar'}
    grapher = Grapher(settings, "dff7843c-567c-4cdb-8000-f7e896f8c6e0")
    grapher.graph()





