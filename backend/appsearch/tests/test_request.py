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

    def test_to_dict(self):
        stats = SearchProgressStats(
            ticketID='test',
            num_items_fetched=50,
            total_items=567,
            average_response_time=1,
            randomPaper='test paper',
            search_state='testing',
            grouping='all',
        )
        self.assertEqual(
            stats.to_dict(),
            {
                'numResultsDiscovered': 567,
                'numResultsRetrieved': 50,
                'progressPercent': (50 / 567) * 100,
                'estimateSecondsToCompletion': None,
                'randomPaper': 'test paper',
                'randomText': None,
                'grouping': 'all',
                'state': 'testing'
            }
        )

    def test_update_progress_all_search(self):
        # given
        stats = SearchProgressStats(
            ticketID='test',
            num_items_fetched=100,
            total_items=1000,
            average_response_time=2,
            grouping='all',
        )
        # when
        stats.update_progress(
            elapsed_time=1,
            num_workers=1,
            xml=b'<test></test>'
        )
        # then
        self.assertEqual(
            stats.to_dict(),
            {
                'numResultsDiscovered': 1000,
                'numResultsRetrieved': 150,
                'progressPercent': (150 / 1000) * 100,
                'estimateSecondsToCompletion': 25.5,
                'randomPaper': '',
                'randomText': None,
                'grouping': 'all',
                'state': 'RUNNING'
            }
        )

    def test_update_response_time_all_search(self):
        stats = SearchProgressStats(
            ticketID='test',
            num_items_fetched=150,
            total_items=1000,
            average_response_time=1.5,
            grouping='all',
        )
        # when
        stats.update_progress(
            elapsed_time=10,
            num_workers=2,
            xml=b'<test></test>'
        )
        # then
        self.assertEqual(
            stats.average_response_time,
            5.75
        )
        self.assertEqual(
            stats.estimate_seconds_to_completion,
            46
        )

    def test_update_progress_grouped_search(self):
        # given
        stats = SearchProgressStats(
            ticketID='test',
            num_items_fetched=100,
            total_items=200,
            average_response_time=2,
            grouping='year',
        )
        # when
        stats.update_progress(
            elapsed_time=1,
            num_workers=1,
            xml=b'<test></test>'
        )
        # then
        self.assertEqual(
            stats.to_dict(),
            {
                'numResultsDiscovered': 200,
                'numResultsRetrieved': 101,
                'progressPercent': (101 / 200) * 100,
                'estimateSecondsToCompletion': 148.5,
                'randomPaper': '',
                'randomText': None,
                'grouping': 'year',
                'state': 'RUNNING'
            }
        )

