from unittest import TestCase
from unittest.mock import MagicMock
from gallica.searchprogressstats import SearchProgressStats


class TestSearchProgressStats(TestCase):

    def setUp(self) -> None:
        self.ticketProgressStats = SearchProgressStats(
            ticketID=1,
            searchType='all',
            parse=MagicMock()
        )
        self.ticketProgressStats.setNumRecordsToFetch(20)

    def test_get(self):
        test = self.ticketProgressStats.get()

        self.assertIsInstance(test, dict)
        self.assertIsInstance(test['numResultsDiscovered'], int)
        self.assertIsInstance(test['numResultsRetrieved'], int)
        self.assertIsInstance(test['progressPercent'], int)
        self.assertIsInstance(test['estimateSecondsToCompletion'], int)
        self.assertIsInstance(test['active'], int)

    def test_update(self):
        self.ticketProgressStats.update(
            progressStats={
                'elapsedTime': 1,
                'numWorkers': 1,
                'xml': MagicMock()
            }
        )

        self.assertEqual(self.ticketProgressStats.numRecordsToFetch, 20)
        self.assertEqual(self.ticketProgressStats.active, 1)
        self.assertEqual(self.ticketProgressStats.numBatches, 1)
        self.assertEqual(self.ticketProgressStats.numBatchesRetrieved, 1)
        self.assertEqual(self.ticketProgressStats.progressPercent, 100)
        self.assertEqual(self.ticketProgressStats.estimateSecondsToCompletion, 0)
