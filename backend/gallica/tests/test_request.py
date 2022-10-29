from unittest import TestCase
from unittest.mock import MagicMock
from gallica.request import Request


class TestRequest(TestCase):

    def setUp(self) -> None:
        self.request = Request(
            identifier=1,
            argsBundles={
                1: {'grouping': 'all'},
                2: {'grouping': 'all'}
            },
            statKeeper=MagicMock(),
            searchBuilder=MagicMock(),
            conn=MagicMock(),
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

    def test_set_ticket_progress_stats(self):
        self.request.searchProgressStats = {
            1: MagicMock(),
            2: MagicMock(),
        }
        self.request.setSearchProgressStats(
            progressStats={'ticketID': 1}
        )
        self.request.searchProgressStats[1].update.assert_called_once()
