from unittest import TestCase
from unittest.mock import MagicMock
from gallica.request import Request


class TestRequest(TestCase):

    def setUp(self) -> None:
        self.request = Request(
            requestID=1,
            argsBundles={
                1: MagicMock(),
                2: MagicMock()
            }
        )

    def test_get_progress_stats(self):
        self.request.searchProgressStats = {
            1: MagicMock(get=MagicMock(return_value='stats')),
            2: MagicMock(get=MagicMock(return_value='stats')),
        }
        self.assertEqual(
            self.request.getProgressStats(),
            {
                1: 'stats',
                2: 'stats',
            }
        )

    def test_run(self):
        self.request.run()

        self.assertEqual(len(self.request.searches), 2)
        self.request.DBconnection.close.assert_called_once()

    def test_set_ticket_progress_stats(self):
        self.request.searchProgressStats = {
            1: MagicMock(),
            2: MagicMock(),
        }
        self.request.setSearchProgressStats(
            ticketID=1,
            progressStats=MagicMock()
        )
        self.request.searchProgressStats[1].update.assert_called_once()
