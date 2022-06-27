import os

from db import DB
from ticketGraphSeriesBatch import TicketGraphSeries
from topPapers import TopPapers


class DBtester:

    def __init__(self):
        self.conn = DB().getConn()

    def getTestSeries(self, timeBin, continuous, averageWindow):
        self.copyTestResults()
        series = TicketGraphSeries(
            "id!",
            {
                "averageWindow": averageWindow,
                "groupBy": timeBin,
                "dateRange": "1900, 1907",
                "continuous": continuous
            },
            self.conn
        )
        testSeries = series.getSeries()
        self.deleteTestResults()
        return testSeries

    def getTestTopPapers(self, continuous, dateRange):
        self.copyTestResults()
        topPapers = TopPapers(
            ticketID='id!',
            continuous=continuous,
            dateRange=dateRange)
        testResults = topPapers.getTopPapers()
        self.deleteTestResults()
        return testResults

    def copyTestResults(self):
        with open(os.path.join(os.path.dirname(__file__), 'data/dummyResults')) as f:
            with self.conn.cursor() as curs:
                curs.copy_from(f, 'results', sep=',', columns=(
                    'identifier',
                    'year',
                    'month',
                    'day',
                    'jstime',
                    'searchterm',
                    'paperid',
                    'requestid'))

    def deleteTestResults(self):
        with self.conn.cursor() as curs:
            curs.execute("""
            DELETE FROM results
            WHERE requestid = 'id!';
            """)

    def deleteAndReturnPaper(self, id):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                DELETE FROM papers
                WHERE code = %s
                RETURNING (title, startdate, enddate, continuous, code)
                """
                , (id,))
            return curs.fetchone()[0]
