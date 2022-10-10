from gallica.factories.requestFactory import RequestFactory
from gallica.request import Request
import unittest


class TestRequestFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.testFactory = RequestFactory(
            tickets={
                'ticket1': {
                    'terms': ['test'],
                    'codes': ['test'],
                    'dateRange': ['test', 'test'],
                    'linkTerm': 'test',
                    'linkDistance': 'test',
                    'fetchType': 'all'
                }
            },
            requestid='test'
        )

    def test_buildRequest(self):
        self.testFactory.buildRequest()
        self.assertIsInstance(self.testFactory.buildRequest(), Request)


if __name__ == '__main__':
    unittest.main()
