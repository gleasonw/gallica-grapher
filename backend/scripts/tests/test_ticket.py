from unittest import TestCase
from unittest.mock import MagicMock, patch
from scripts.ticket import Ticket

import scripts.ticket


class TestTicket(TestCase):


    @patch('scripts.ticket.Ticket.initQueryObjects')
    @patch('scripts.ticket.Ticket.sumResultsOfEachQuery')
    def test_getEstimateNumberRecords(self, mock_sum_results, mock_init):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.totalResults = 512

        self.assertEqual(ticket.getEstimateNumberRecords(), 512)
        mock_sum_results.assert_called_once()
        mock_init.assert_called_with(ticket.genAllPaperQuery)

    @patch('scripts.ticket.Ticket.initQueryObjects')
    @patch('scripts.ticket.Ticket.sumResultsOfEachQuery')
    def test_get_Estimate_Number_Records_Paper_Ticket(self, mock_sum_results, mock_init):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': ['test'],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.totalResults = 512

        self.assertEqual(ticket.getEstimateNumberRecords(), 512)
        mock_sum_results.assert_called_once()
        mock_init.assert_called_with(ticket.genSelectPaperQuery)

    @patch("scripts.ticket.Ticket.addKeywordAndTicketIDToRecords")
    def test_run(self, mock_add):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.termQueries = [
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock())
        ]
        ticket.totalResults = 512
        mock_add.return_value = [1, 2, 3]

        ticket.run()

        self.assertEqual(ticket.numBatches, 11)
        for query in ticket.termQueries:
            query.runSearch.assert_called_once()
        mock_add.assert_called()
        self.assertListEqual(ticket.records, [1, 2, 3, 1, 2, 3, 1, 2, 3])

    def test_add_keyword_and_ticket_id_to_records(self):
        testTicket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        testTicket.ticketID = 'testTicketID'
        mockRecord = MagicMock(
            setKeyword=MagicMock(),
            setTicketID=MagicMock())
        testRecords = [mockRecord, mockRecord, mockRecord]

        modifiedRecords = testTicket.addKeywordAndTicketIDToRecords(testRecords, 'test')

        mockRecord.setKeyword.assert_called_with('test')
        mockRecord.setTicketID.assert_called_with('testTicketID')
        self.assertEqual(len(modifiedRecords), 3)




    def test_init_query_objects(self):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': ['test'],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.terms = [MagicMock, MagicMock, MagicMock]
        ticket.initQueryObjects(MagicMock(return_value=MagicMock()))
        self.assertEqual(len(ticket.termQueries), 3)

    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.buildQuery")
    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults")
    def test_gen_select_paper_query(self, mock_build, mock_fetch):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': {"paper": "", "code": 'test'},
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())

        testQuery = ticket.genSelectPaperQuery(ticket.terms[0])

        self.assertIsInstance(testQuery, scripts.ticket.NgramQueryWithConcurrencySelectPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertDictEqual(testQuery.paperCodes, {"paper": "", "code": 'test'})
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencyAllPapers.buildQuery")
    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencyAllPapers.fetchNumTotalResults")
    def test_gen_all_paper_query(self, mock_build, mock_fetch):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())

        testQuery = ticket.genAllPaperQuery(ticket.terms[0])

        self.assertIsInstance(testQuery, scripts.ticket.NgramQueryWithConcurrencyAllPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    def test_sum_results_of_each_ticket(self):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.termQueries=[
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=10)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=11)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=12))
        ]
        ticket.sumResultsOfEachQuery()

        self.assertEqual(ticket.totalResults, 33)

    def test_update_progress(self):
        ticket = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(setProgress=MagicMock()),
            MagicMock(),
            MagicMock())
        ticket.numBatchesRetrieved = 2
        ticket.numBatches = 10

        ticket.updateProgressStats('the seattle times', 10, 50)

        ticket.progressThread.setTicketProgressStats.assert_called_with(
            "",
            {
                'progress': 30,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 150,
                'randomPaper': 'the seattle times',
                'estimateSecondsToCompletion': 7 / 50 * 10
            }
        )

        ticket.updateProgressStats('le figaro', 90, 50)

        ticket.progressThread.setTicketProgressStats.assert_called_with(
            "",
            {
                'progress': 40,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 200,
                'randomPaper': 'le figaro',
                'estimateSecondsToCompletion': 6 / 50 * 50
            }
        )



