from unittest import TestCase
from api.requestThread import RequestThread


class TestRequestThread(TestCase):
    def test_run(self):
        request = RequestThread({
            '4321': {
                "terms": ["brazza"],
                "papersAndCodes": [],
                "dateRange": [1850, 1900],
            }
        }

        )
        request.run()

