from unittest import TestCase
from api.requestThread import RequestThread


class TestRequestThread(TestCase):
    def test_run(self):
        request = RequestThread([
            {
                "terms": ["malamine"],
                "papersAndCodes": [],
                "dateRange": [1800, 1900],
                "id": '12345'
            }
        ])
        request.run()

