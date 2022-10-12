from unittest import TestCase
from unittest.mock import MagicMock
from gallica.ticketprogressstats import TicketProgressStats


class TestTicketProgressStats(TestCase):

    def setUp(self) -> None:
        self.ticketProgressStats = TicketProgressStats(ticketID=1)

    def test_get(self):
        test = self.ticketProgressStats.get()

        self.assertIsInstance(test, dict)
        self.assertIsInstance(test['numResultsDiscovered'], int)
        self.assertIsInstance(test['numResultsRetrieved'], int)
        self.assertIsInstance(test['progressPercent'], int)
        self.assertIsInstance(test['estimateSecondsToCompletion'], int)
        self.assertIsNone(test['randomPaperForDisplay'])
        self.assertIsNone(test['randomTextForDisplay'])
        self.assertIsInstance(test['active'], int)

    def test_update(self):
        self.ticketProgressStats.update(
            progressStats={
                'elapsedTime': 1,
                'numWorkers': 1,
                'randomPaper': MagicMock(),
                'randomTextForDisplay': MagicMock(),
                'numResultsDiscovered': 5
            }
        )

        self.assertEqual(self.ticketProgressStats.numResultsDiscovered, 5)
        self.assertEqual(self.ticketProgressStats.active, 1)
        self.assertEqual(self.ticketProgressStats.numBatches, 1)
        self.assertEqual(self.ticketProgressStats.numBatchesRetrieved, 1)
