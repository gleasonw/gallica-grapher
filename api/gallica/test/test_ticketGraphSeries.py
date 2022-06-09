from unittest import TestCase
from gallica.ticketGraphSeries import TicketGraphSeries
import psycopg2

class TestTicketGraphSeries(TestCase):
    def test_get_series(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        series = TicketGraphSeries('1234',dbConnection=conn,groupby='day')
        print(series.getSeries())