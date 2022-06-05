from unittest import TestCase
from requestThread import RequestThread


class TestRequestThread(TestCase):
    def test_run(self):
        request = RequestThread([
            {
                "terms": ["brazza","malamine"],
                "papersAndCodes": [{"paper": "Le Petit Journal",
                                    "code": "cb32895690j"}],
                "dateRange": [1800, 1900],
                "id": '12345'
            },
            {
                "terms": ["croissant"],
                "papersAndCodes": [{"paper": "Le Petit Journal",
                                    "code": "cb32895690j"}],
                "dateRange": [1800, 1900],
                "id": '12345'
            }
        ])
        request.run()

