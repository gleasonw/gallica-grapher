from unittest import TestCase
from unittest.mock import patch, MagicMock
from backend.tasks import spawnRequest


class TestSpawnRequest(TestCase):

    @patch("backend.tasks.Request")
    def test_success(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = True

        returnTest = spawnRequest("test")

        self.assertEqual(returnTest["status"], "Complete!")
        self.assertEqual(returnTest["result"], 42)

    @patch("backend.tasks.Request")
    def test_too_many_records(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = False
        mock_request.tooManyRecords = True
        mock_request.estimateNumRecords = 100

        returnTest = spawnRequest("test")

        self.assertEqual(returnTest["status"], "Too many records!")
        self.assertEqual(returnTest["numRecords"], 100)

    @patch("backend.tasks.Request")
    def test_progress(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = False
        mock_request.tooManyRecords = False
        mock_request.getProgressStats.return_value = {
            "progress": 0,
            "numResultsDiscovered": 0,
            "numResultsRetrieved": 0,
            "randomPaper": None,
            "estimateSecondsToCompletion": 0
        }

        returnTest = spawnRequest("test")

        self.assertEqual(returnTest["status"], "PROGRESS")
        self.assertEqual(returnTest["meta"]["progress"], {
            "progress": 0,
            "numResultsDiscovered": 0,
            "numResultsRetrieved": 0,
            "randomPaper": None,
            "estimateSecondsToCompletion": 0
        })