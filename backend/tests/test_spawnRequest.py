from unittest import TestCase
from unittest.mock import patch, MagicMock
from backend.tasks import spawnRequest


class TestSpawnRequest(TestCase):

    @patch("backend.tasks.Request")
    def test_success(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = True

        returnTest = spawnRequest("tests")

        self.assertEqual(returnTest["status"], "Complete!")
        self.assertEqual(returnTest["result"], 42)

    @patch("backend.tasks.Request")
    def test_too_many_records(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = False
        mock_request.tooManyRecords = True
        mock_request.estimateNumRecords = 100

        returnTest = spawnRequest("tests")

        self.assertEqual(returnTest["status"], "Too many records!")
        self.assertEqual(returnTest["numRecords"], 100)

    @patch("backend.tasks.Request")
    def test_progress(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = False
        mock_request.tooManyRecords = False

        with self.assertRaises(TypeError):
            spawnRequest("tests")
