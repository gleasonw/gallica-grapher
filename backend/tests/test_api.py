import api.api as flaskAPI
import unittest
from unittest.mock import patch, MagicMock
import json


class TestAPI(unittest.TestCase):

    def setUp(self):
        flaskAPI.app.config['TESTING'] = True
        self.app = flaskAPI.app.test_client()

    @patch("api.flaskAPI.spawnRequestThread.delay")
    def test_init(self, mock_spawnRequestThread):
        mock_spawnRequestThread.return_value = MagicMock(id="test")
        response = self.app.post(
            '/init',
            json={'tickets': {}})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['taskid'], "test")

    @patch("api.flaskAPI.spawnRequestThread.AsyncResult")
    def test_get_pending_state(self, mock_task):
        mock_task.return_value = MagicMock(
            state="PENDING",
            info={"progress": 0, "currentID": ""}
        )
        response = self.app.get('/progress/test')
        jsonResponse = json.loads(response.data)

        self.assertEqual(jsonResponse["state"], "PENDING")

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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"series":[]}\n')

    @patch("api.flaskAPI.TopPapers")
    def test_getTopPapersFromID(self, mock_topPapers):
        mockedTopPapers = mock_topPapers.return_value
        mockedTopPapers.getTopPapers.return_value = []
        query = 'topPapers?id=test&continuous=test&dateRange=test'
        testTopPapersFromID = self.app.get(query)

        assert testTopPapersFromID.status_code == 200
        self.assertEqual(testTopPapersFromID.data, b'{"topPapers":[]}\n')

    @patch("api.flaskAPI.spawnRequestThread")
    def test_getProgress(self, mock_celery_task):
        mock_celery_task.return_value = mock_celery_task
        mock_celery_task.AsyncResult.return_value = mock_celery_task
        mock_celery_task.info = MagicMock(
            get=MagicMock(
                return_value={
                    'progress': 0,
                    'numResultsDiscovered': 0,
                    'numResultsRetrieved': 0,
                    'randomPaper': None,
                    'estimateSecondsToCompletion': 0
                }
            ))
        mock_celery_task.state = "PENDING"

        response = self.app.get('/progress/test')

        self.assertEqual(
            {
                "state": "PENDING",
                "progress": {
                    'progress': 0,
                    'numResultsDiscovered': 0,
                    'numResultsRetrieved': 0,
                    'randomPaper': None,
                    'estimateSecondsToCompletion': 0
                }
            },
            response.json
        )

    @patch("api.flaskAPI.spawnRequestThread")
    def test_getProgress_when_task_null(self, mock_celery_task):
        mock_celery_task.return_value = mock_celery_task
        mock_celery_task.AsyncResult.return_value = mock_celery_task
        mock_celery_task.info = None
        mock_celery_task.state = "PENDING"

        response = self.app.get('/progress/test')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {
                "state": "PENDING",
                'progress': None
            },
            response.json)

