from unittest import TestCase
from ticketGraphSeriesBatch import TicketGraphSeriesBatch


class TestTicketGraphSeriesBatch(TestCase):
    def test_get_series(self):
        settings = {
            "ticketIDs": "4321,1234",
            'averageWindow': "0",
            'groupBy': "month",
            'continuous': "false",
            'dateRange': "1800,1900"
        }
        batch = TicketGraphSeriesBatch(settings)
        print(batch.getSeries())
