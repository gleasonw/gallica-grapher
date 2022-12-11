from unittest import TestCase
from unittest.mock import MagicMock
from appsearch.request import (
    Request,
    get_num_periods_in_range_for_grouping,
    SearchProgressStats
)


class TestRequest(TestCase):

    def setUp(self) -> None:
        self.request = Request(
            identifier=1,
            arg_bundles={
                1: {'terms': 'nice', 'grouping': 'all'},
                2: {'terms': 'nice', 'grouping': 'all'}
            },
            conn=MagicMock()
        )

    def test_get_progress_stats(self):
        self.request.progress_stats = {
            1: MagicMock(to_dict=MagicMock(return_value='stats')),
            2: MagicMock(to_dict=MagicMock(return_value='stats')),
        }
        self.assertEqual(
            self.request.get_progress_stats(),
            {
                1: 'stats',
                2: 'stats',
            }
        )

    def test_get_num_periods_in_range_for_grouping(self):
        self.assertEqual(
            get_num_periods_in_range_for_grouping(
                grouping='year',
                start='1900',
                end='1908'
            ),
            9
        )
        self.assertEqual(
            get_num_periods_in_range_for_grouping(
                grouping='month',
                start='1900',
                end='1908'
            ),
            108
        )


class TestSearchProgressStats(TestCase):
    def setUp(self) -> None:
        self.stats = SearchProgressStats(
            ticketID='test',
            num_items_fetched=1,
            total_items=567,
            average_response_time=1,
            randomPaper='test paper',
            search_state='testing'
        )

    def test_to_dict(self):
        self.assertEqual(
            self.stats.to_dict(),
            {
                'numResultsDiscovered': 567,
                'numResultsRetrieved': 50,
                'progressPercent': 1/12,
                'estimateSecondsToCompletion': None,
                'randomPaper': 'test paper',
                'randomText': None,
                'active': False
            }
        )

    def test_update_progress(self):
        #given
        stats = SearchProgressStats(
            ticketID='test',
            num_items_fetched=2,
            total_items=1000,
            average_response_time=2,
        )
        #when
        stats.update_progress(
            elapsed_time=1,
            num_workers=1,
            xml=b'<test></test>'
        )
        #then
        self.assertEqual(
            stats.to_dict(),
            {
                'numResultsDiscovered': 1000,
                'numResultsRetrieved': 150,
                'progressPercent': 3/21,
                'estimateSecondsToCompletion': 27,
                'randomPaper': '',
                'randomText': None,
                'active': True
            }
        )
        #when
        stats.update_progress(
            elapsed_time=10,
            num_workers=2,
            xml=b'<test></test>'
        )
        #then
        self.assertEqual(
            stats.to_dict(),
            {
                'numResultsDiscovered': 1000,
                'numResultsRetrieved': 200,
                'progressPercent': 4/21,
                'estimateSecondsToCompletion': 48.875,
                'randomPaper': '',
                'randomText': None,
                'active': True
            }
        )
