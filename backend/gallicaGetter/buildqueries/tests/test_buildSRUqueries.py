from unittest import TestCase
from gallicaGetter.buildqueries.buildSRUqueries import build_base_queries
from gallicaGetter.fetch.query import OccurrenceQuery
from unittest.mock import MagicMock


class Test(TestCase):
    def setUp(self) -> None:
        self.month_args = {
            'terms': 'test',
            'codes': 'test',
            'startDate': '1980',
            'endDate': '1985',
            'grouping': 'month',
        }
        self.endpoint_url = 'test'
        self.api = MagicMock(get=lambda x: [
            MagicMock(query=i, data='test')
            for i in x
        ])
        self.query_cache = 'test'

    def test_build_queries(self):
        test = build_base_queries(self.month_args, endpoint_url=self.endpoint_url, api=self.api)
        print(test)

