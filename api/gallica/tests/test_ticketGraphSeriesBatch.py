import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from ticketGraphSeriesBatch import TicketGraphSeriesBatch
from ticketGraphSeriesBatch import TicketGraphSeries
from ticketGraphSeriesBatch import parseContinuous
from gallica.db import DB


class TestTicketGraphSeriesBatch(TestCase):

    @patch("psycopg2.connect")
    @patch("ticketGraphSeriesBatch.TicketGraphSeriesBatch.selectAllSeriesFromDB")
    def test_get_series_batch(self, mock_select, mock_db):
        batch = TicketGraphSeriesBatch({"ticketIDs": ''})
        batch.dataBatches = [
            ['a', [1]],
            ['b', [1]]
        ]
        testBatch = batch.getSeriesBatch()
        self.assertDictEqual(
            testBatch,
            {'a': [1],
             'b': [1]}
        )
        batch.dataBatches = []
        emptyTestBatch = batch.getSeriesBatch()
        self.assertDictEqual(emptyTestBatch, {})

    @patch("psycopg2.connect")
    @patch("ticketGraphSeriesBatch.TicketGraphSeriesBatch.selectOneSeries")
    def test_select_all_series_from_db(self, mock_select, mock_connect):
        mock_select.return_value = 'neat'
        batch = TicketGraphSeriesBatch({"ticketIDs": '1234,4321'})

        batch.selectAllSeriesFromDB()

        self.assertListEqual(batch.requestIDs, ['1234', '4321'])
        self.assertListEqual(batch.dataBatches, ['neat', 'neat'])

    @patch("ticketGraphSeriesBatch.TicketGraphSeries", getSeries=MagicMock(return_value=[1, 2, 3]))
    @patch("ticketGraphSeriesBatch.TicketGraphSeriesBatch.selectAllSeriesFromDB")
    @patch("psycopg2.connect")
    def test_select_one_series(self,mock_connect, mock_select, mock_series):
        mock_series.return_value = MagicMock(getSeries=MagicMock(return_value='nice'))
        batch = TicketGraphSeriesBatch({"ticketIDs": 'neat'})
        testSeries = batch.selectOneSeries(batch.requestIDs[0])
        self.assertListEqual(testSeries, ["neat","nice"])


class TestTicketGraphSeries(TestCase):

    def test_parse_continuous(self):
        self.assertFalse(parseContinuous(""))
        self.assertFalse(parseContinuous("false"))
        self.assertTrue(parseContinuous("true"))
        self.assertTrue(parseContinuous("TruE"))

    @patch("ticketGraphSeriesBatch.TicketGraphSeries.makeSeries")
    def test_get_series(self, mock_make):
        testSeries = TicketGraphSeries(
            "neat",
            {
                "averageWindow": 5,
                "groupBy": 'month',
                "dateRange": "1890, 1900",
                "continuous": "false"
            },
            MagicMock()
        )
        test = testSeries.getSeries()

        self.assertDictEqual(
            test,
            {'name':[],'data':[]}
        )

    @patch("ticketGraphSeriesBatch.TicketGraphSeries.buildQueryForSeries")
    @patch("ticketGraphSeriesBatch.TicketGraphSeries.runQuery")
    def test_make_series(self, mock_run, mock_build):
        testSeries = TicketGraphSeries(
            "neat",
            {
                "averageWindow": 5,
                "groupBy": 'month',
                "dateRange": "1890, 1900",
                "continuous": "false"
            },
            MagicMock()
        )
        mock_run.assert_called_once()
        mock_build.assert_called_once()

    @patch("ticketGraphSeriesBatch.TicketGraphSeries.initDayRequest")
    @patch("ticketGraphSeriesBatch.TicketGraphSeries.initMonthRequest")
    @patch("ticketGraphSeriesBatch.TicketGraphSeries.initYearRequest")
    @patch("ticketGraphSeriesBatch.TicketGraphSeries.initDayContinuousPaperRequest")
    @patch("ticketGraphSeriesBatch.TicketGraphSeries.initMonthContinuousPaperRequest")
    @patch("ticketGraphSeriesBatch.TicketGraphSeries.initYearContinuousPaperRequest")
    @patch("ticketGraphSeriesBatch.TicketGraphSeries.makeSeries")
    def test_build_query_for_series(
            self,
            mock_make,
            mock_initYearContinuous,
            mock_initMonthContinuous,
            mock_initDayContinuous,
            mock_initYear,
            mock_initMonth,
            mock_initDay
    ):
        testSeries = TicketGraphSeries(
            "neat",
            {
                "averageWindow": 5,
                "groupBy": 'day',
                "dateRange": "1890, 1900",
                "continuous": "false"
            },
            MagicMock()
        )

        testSeries.buildQueryForSeries()
        mock_initDay.assert_called_once()

        testSeries.timeBin = 'month'
        testSeries.buildQueryForSeries()
        mock_initMonth.assert_called_once()

        testSeries.timeBin = 'year'
        testSeries.buildQueryForSeries()
        mock_initYear.assert_called_once()

        testSeries.continuous = True
        testSeries.buildQueryForSeries()
        mock_initYearContinuous.assert_called_once()

        testSeries.timeBin = 'month'
        testSeries.buildQueryForSeries()
        mock_initMonthContinuous.assert_called_once()

        testSeries.timeBin = 'day'
        testSeries.buildQueryForSeries()
        mock_initDayContinuous.assert_called_once()

    @staticmethod
    def getTestSeries(timeBin, continuous, averageWindow):
        conn = DB().getConn()
        with open(os.path.join(os.path.dirname(__file__), 'data/dummyResults')) as f:
            with conn.cursor() as curs:
                curs.copy_from(f, 'results', sep=',', columns=(
                        'identifier',
                        'year',
                        'month',
                        'day',
                        'jstime',
                        'searchterm',
                        'paperid',
                        'requestid'))
                series = TicketGraphSeries(
                    "id!",
                    {
                        "averageWindow": averageWindow,
                        "groupBy": timeBin,
                        "dateRange": "1900, 1907",
                        "continuous": continuous
                    },
                    conn
                )
                testSeries = series.getSeries()
                curs.execute("""
                DELETE FROM results
                WHERE requestid = 'id!';
                """)
                return testSeries

    def test_day_binned_request(self):

        testSeries = TestTicketGraphSeries.getTestSeries('day', 'false', 0)

        self.assertIsNotNone(testSeries["name"])
        self.assertIsNotNone(testSeries["data"])
        self.assertListEqual(
            testSeries["name"],
            ['brazza', 'brazzaWack'])
        self.assertEqual(
            len(testSeries["data"]),
            9)

    def test_day_binned_continuous_request(self):

        testSeries = TestTicketGraphSeries.getTestSeries('day', 'true', 0)

        self.assertIsNotNone(testSeries["name"])
        self.assertIsNotNone(testSeries["data"])
        self.assertListEqual(
            testSeries["name"],
            ['brazza', 'brazzaWack'])
        self.assertEqual(
            len(testSeries["data"]),
            7)

    def test_month_binned_request(self):

            testSeries = TestTicketGraphSeries.getTestSeries('month', 'false', 0)

            self.assertIsNotNone(testSeries["name"])
            self.assertIsNotNone(testSeries["data"])
            self.assertListEqual(
                testSeries["name"],
                ['brazza', 'brazzaWack'])
            self.assertEqual(
                len(testSeries["data"]),
                8)

    def test_month_binned_continuous_request(self):

        testSeries = TestTicketGraphSeries.getTestSeries('month', 'true', 0)

        self.assertIsNotNone(testSeries["name"])
        self.assertIsNotNone(testSeries["data"])
        self.assertListEqual(
            testSeries["name"],
            ['brazza', 'brazzaWack'])
        self.assertEqual(
            len(testSeries["data"]),
            7)

    def test_year_binned_request(self):
        testSeries = TestTicketGraphSeries.getTestSeries('year', 'false', 0)

        self.assertIsNotNone(testSeries["name"])
        self.assertIsNotNone(testSeries["data"])
        self.assertListEqual(
            testSeries["name"],
            ['brazza', 'brazzaWack'])
        self.assertEqual(
            len(testSeries["data"]),
            8)

    def test_year_binned_continuous_request(self):
        testSeries = TestTicketGraphSeries.getTestSeries('year', 'true', 0)

        self.assertIsNotNone(testSeries["name"])
        self.assertIsNotNone(testSeries["data"])
        self.assertListEqual(
            testSeries["name"],
            ['brazza', 'brazzaWack'])
        self.assertEqual(
            len(testSeries["data"]),
            7)

    def test_rolling_average(self):

        testSeries = TestTicketGraphSeries.getTestSeries('year', 'false', 1)

        self.assertIsNotNone(testSeries["name"])
        self.assertIsNotNone(testSeries["data"])
        self.assertListEqual(
            testSeries["name"],
            ['brazza', 'brazzaWack'])
        testRolledAverage = testSeries["data"][3][1]
        self.assertEqual(
            testRolledAverage,
            2.5)

        testSeries = TestTicketGraphSeries.getTestSeries('year', 'false', 3)

        testRolledAverage = testSeries["data"][3][1]
        self.assertEqual(
            testRolledAverage,
            2.25)









