from unittest import TestCase
from unittest.mock import MagicMock
from appsearch.request import (
    Request,
    get_num_periods_in_range_for_grouping
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

    def test_run(self):
        self.request.run()