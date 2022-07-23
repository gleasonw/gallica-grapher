from unittest import TestCase
from unittest.mock import patch, MagicMock
from requestThread import RequestThread
from gallica.requestTicket import RequestTicket


class TestRequestThread(TestCase):

    def test_init(self):
        testThread = RequestThread({})
        self.assertIsInstance(testThread, RequestThread)

    @patch("requestThread.RequestTicket")
    def test_run(self, mock_ticket):
        mock_ticket.return_value = MagicMock(run=MagicMock())
        testThread = RequestThread({'1': {}})
        testThread.DBconnection = MagicMock(close=MagicMock())

        testThread.run()

        mock_ticket.assert_called_once()
        mock_ticket.return_value.run.assert_called_once()
        testThread.DBconnection.close.assert_called_once()
        self.assertEqual(testThread.currentID, '1')

    def test_set_progress(self):
        testThread = RequestThread({})

        testThread.setProgress(10)

        self.assertEqual(testThread.keyedProgress, 10)

    def test_get_progress(self):
        testThread = RequestThread({})

        self.assertEqual(testThread.getKeyedProgress()['progress'], 0)

    def test_set_num_discovered(self):
        testThread = RequestThread({})

        testThread.setNumDiscovered(10)

        self.assertEqual(testThread.numResultsDiscovered, 10)

    def test_get_num_discovered(self):
        testThread = RequestThread({})

        self.assertEqual(testThread.getNumDiscovered(), 0)

    def test_set_num_actually_retrieved(self):
        testThread = RequestThread({})

        testThread.setNumActuallyRetrieved(10)

        self.assertEqual(testThread.numResultsRetrieved, 10)

    def test_get_num_actually_retrieved(self):
        testThread = RequestThread({})

        self.assertEqual(testThread.getNumActuallyRetrieved(), 0)
