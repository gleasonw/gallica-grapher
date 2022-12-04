from unittest import TestCase
from unittest.mock import MagicMock
from appsearch.request import SearchProgressStats


class TestSearchProgressStats(TestCase):

    def setUp(self) -> None:
        self.ticketProgressStats = SearchProgressStats(
            ticketID=1,
            grouping='all',
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
        self.assertIsInstance(test['state'], str)

    def test_update(self):
        self.ticketProgressStats.update(
            progressStats={
                'elapsedTime': 1,
                'numWorkers': 1,
                'xml': MagicMock()
            }
        )

        self.assertEqual(self.ticketProgressStats.numRecordsToFetch, 20)
        self.assertEqual(self.ticketProgressStats.state, 'RUNNING')
        self.assertEqual(self.ticketProgressStats.numBatches, 1)
        self.assertEqual(self.ticketProgressStats.num_retrieved_batches, 1)
        self.assertEqual(self.ticketProgressStats.progressPercent, 100)
        self.assertEqual(self.ticketProgressStats.estimateSecondsToCompletion, 0)
