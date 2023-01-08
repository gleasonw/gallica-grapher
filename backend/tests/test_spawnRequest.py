from unittest import TestCase
from unittest.mock import patch, MagicMock
from backend.tasks import spawn_request


class TestSpawnRequest(TestCase):
    @patch("backend.tasks.Request")
    def test_success(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = True

        returnTest = spawn_request("tests")

        self.assertEqual(returnTest["status"], "Complete!")
        self.assertEqual(returnTest["result"], 42)

    @patch("backend.tasks.Request")
    def test_too_many_records(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = False
        mock_request.tooManyRecords = True
        mock_request.sum_records_for_searches = 100

        returnTest = spawn_request("tests")

        self.assertEqual(returnTest["status"], "Too many records!")
        self.assertEqual(returnTest["getNumRecords"], 100)

    @patch("backend.tasks.Request")
    def test_progress(self, mock_request):
        mock_request.return_value = mock_request
        mock_request.finished = False
        mock_request.tooManyRecords = False

        with self.assertRaises(TypeError):
            spawn_request("tests")
