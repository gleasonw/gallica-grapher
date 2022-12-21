import backend.api as flaskAPI
import unittest
from unittest.mock import patch, MagicMock
import json


class TestAPI(unittest.TestCase):

    def setUp(self):
        flaskAPI.app.config['TESTING'] = True
        self.app = flaskAPI.app.test_client()

    @patch("backend.api.spawnRequest.delay")
    def test_init(self, mock_spawnRequestThread):
        mock_spawnRequestThread.return_value = MagicMock(id="tests")
        response = self.app.post(
            '/api/init',
            json={'tickets': {}})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['taskid'], "tests")

    def test_paperChart(self):
        testJSON = self.app.get('/api/paperchartjson')

        assert testJSON.status_code == 200
        self.assertIsNotNone(testJSON.data)

    def test_papers(self):
        testPapersSimilarToKeyword = self.app.get('/api/papers/tests')

        assert testPapersSimilarToKeyword.status_code == 200
        self.assertIsNotNone(testPapersSimilarToKeyword)

    @patch('backend.api.PaperLocalSearch')
    def test_get_num_papers_over_range(self, mock_search):
        mock_search.getNumPapersInRange = MagicMock(return_value=1)
        mock_search.return_value = mock_search

        testNumPapersOverRange = self.app.get('/api/numPapersOverRange/0/100')

        mock_search.getNumPapersInRange.assert_called_once_with('0', '100')
        assert testNumPapersOverRange.status_code == 200
        self.assertEqual(testNumPapersOverRange.json['numPapersOverRange'], 1)

    @patch('backend.api.PaperLocalSearch')
    def test_get_continuous_papers_over_range(self, mock_search):
        mock_search.select_continuous_papers = MagicMock(return_value=1)
        mock_search.return_value = mock_search

        testContinuousPapersOverRange = self.app.get('/api/continuousPapers?limit=1&startDate=0&endDate=100')

        mock_search.select_continuous_papers.assert_called_once_with('0', '100', '1')
        assert testContinuousPapersOverRange.status_code == 200
        self.assertEqual(testContinuousPapersOverRange.json['continuousPapers'], 1)

    @patch("backend.api.TicketGraphSeriesBatch")
    def test_getGraphData(self, mock_series):
        mockedSeries = mock_series.return_value
        mockedSeries.select_series_for_tickets.return_value = []
        query = '/api/graphData?keys=tests&averageWindow=tests&timeBin=tests&continuous=tests&dateRange=tests'

        response = self.app.get(query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"series":[]}\n')

    @patch("backend.api.TopPapersForTicket")
    def test_getTopPapersFromID(self, mock_topPapers):
        mockedTopPapers = mock_topPapers.return_value
        getTopPapers.return_value = []
        query = '/api/topPapers?id=tests&continuous=tests&dateRange=tests'

        testTopPapersFromID = self.app.get(query)

        assert testTopPapersFromID.status_code == 200
        self.assertEqual(testTopPapersFromID.data, b'{"topPapers":[]}\n')

    @patch("backend.api.ReactCSVdata")
    def test_get_csv(self, mock_csv):
        mock_csv.getCSVData.return_value = []
        mock_csv.return_value = mock_csv
        query = '/api/getcsv?tickets=""'

        response = self.app.get(query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"csvData":[]}\n')

    @patch("backend.api.spawnRequest")
    def test_getProgress_when_task_in_progress(self, mock_celery_task):
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
        mock_celery_task.state = "PROGRESS"

        response = self.app.get('/api/progress/tests')

        self.assertEqual(
            {
                "state": "PROGRESS",
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

    @patch("backend.api.spawnRequest")
    def test_getProgress_when_task_success_result_null(self, mock_celery_task):
        mock_celery_task.return_value = mock_celery_task
        mock_celery_task.AsyncResult.return_value = mock_celery_task
        mock_celery_task.state = "SUCCESS"

        response = self.app.get('/api/progress/tests')

        self.assertEqual(response.status_code, 200)
        self.assertEqual({"state": "SUCCESS"}, response.json)

    @patch("backend.api.spawnRequest")
    def test_getProgress_when_too_many_records(self, mock_celery_task):
        mock_celery_task.return_value = mock_celery_task
        mock_celery_task.AsyncResult.return_value = mock_celery_task
        mock_celery_task.state = "SUCCESS"
        mock_celery_task.result = {
            "status": "Too many records!",
            "getNumRecords": 100
        }

        response = self.app.get('/api/progress/tests')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {
                'state': 'TOO_MANY_RECORDS',
                'getNumRecords': 100
            },
            response.json
        )


