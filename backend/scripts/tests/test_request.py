from unittest import TestCase
from unittest.mock import patch, MagicMock
from request import Request


class TestRequest(TestCase):

    def test_init(self):
        testThread = Request({}, '1')
        self.assertIsInstance(testThread, Request)

    @patch('request.Request.estimateIsUnderRecordLimit')
    @patch("request.Request.generateRequestTickets")
    @patch("request.Ticket")
    def test_run(
            self,
            mock_ticket,
            mock_generate,
            mock_check_estimate,
    ):
        mock_ticket.run = MagicMock()
        mock_ticket.getEstimateNumberRecords = MagicMock(return_value=10)
        mock_generate.return_value = [mock_ticket]
        testThread = Request({'1': {}}, 'myrequestid')

        testThread.run()

        mock_check_estimate.assert_called_with(10)
        mock_ticket.run.assert_called_once()

    @patch('request.Ticket')
    def test_generate_request_tickets(self, mock_ticket):
        mock_ticket.return_value = mock_ticket
        testRequest = Request({}, '1')
        testRequest.ticketDicts = {
            '1': {},
            '2': {}
        }

        generatedTickets = testRequest.generateRequestTickets()

        self.assertEqual(len(generatedTickets), 2)
        self.assertEqual(generatedTickets[0], mock_ticket)

    @patch('request.Request.getNumberRowsInAllTables')
    def test_estimate_is_under_record_limit(self, mock_get):
        testThread = Request({}, '1')
        mock_get.return_value = 1000000

        self.assertTrue(testThread.estimateIsUnderRecordLimit(100))
        self.assertFalse(testThread.estimateIsUnderRecordLimit(100000000))

    def test_set_progress(self):
        testThread = Request({}, '1')

        testThread.setTicketProgressStats('1', 10)

        self.assertEqual(testThread.ticketProgressStats['1'], 10)

    def test_get_progress(self):
        testThread = Request({'1': {}}, '1')

        self.assertEqual(
            testThread.getProgressStats()['1'],
            {
                'progress': 0,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 0,
                'randomPaper': None,
                'estimateSecondsToCompletion': 0
            }
        )

    def test_set_num_discovered(self):
        testThread = Request({}, '1')

        testThread.setNumDiscovered(10)

        self.assertEqual(testThread.numResultsDiscovered, 10)

    def test_get_num_discovered(self):
        testThread = Request({}, '1')

        self.assertEqual(testThread.getNumDiscovered(), 0)

    def test_set_num_actually_retrieved(self):
        testThread = Request({}, '1')

        testThread.setNumActuallyRetrieved(10)

        self.assertEqual(testThread.numResultsRetrieved, 10)

    def test_get_num_actually_retrieved(self):
        testThread = Request({}, '1')

        self.assertEqual(testThread.getNumActuallyRetrieved(), 0)
