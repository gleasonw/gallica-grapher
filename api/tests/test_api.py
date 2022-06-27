import api.flaskAPI as flaskAPI
import unittest
from unittest.mock import patch, MagicMock


class TestAPI(unittest.TestCase):

    def setUp(self):
        flaskAPI.app.config['TESTING'] = True
        self.app = flaskAPI.app.test_client()

    def test_init(self):
        assert True

    def test_getProgress(self):
        assert True

    def test_paperChart(self):
        testJSON = self.app.get('/paperchartjson')

        assert testJSON.status_code == 200
        self.assertIsNotNone(testJSON.data)

    def test_papers(self):
        testPapersSimilarToKeyword = self.app.get('/papers/test')

        assert testPapersSimilarToKeyword.status_code == 200
        self.assertIsNotNone(testPapersSimilarToKeyword)

    @patch("api.flaskAPI.TicketGraphSeriesBatch")
    def test_getGraphData(self, mock_series):
        mockedSeries = mock_series.return_value
        mockedSeries.getSeriesBatch.return_value = []
        query = 'graphData?keys=test&averageWindow=test&timeBin=test&continuous=test&dateRange=test'
        response = self.app.get(query)

        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data,b'{"series":[]}\n')

    def test_getTopPapersFromID(self):
        assert True