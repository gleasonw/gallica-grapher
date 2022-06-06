from unittest import TestCase
from api.requestThread import RequestThread


class TestRequestThread(TestCase):
    def test_run(self):
        request = RequestThread({
            '1234': {
                "terms": ["malamine"],
                "papersAndCodes": [],
                "dateRange": [1800, 1900],
            }
        }

        )
        request.run()

