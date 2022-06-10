from unittest import TestCase
from gallica.ticketGraphSeriesBatch import TicketGraphSeriesBatch


class TestTicketGraphSeries(TestCase):
    def test_get_graph_json(self):
        graphData = TicketGraphSeriesBatch(
            '1234',
            averagewindow=0,
            groupby='year'
        )
        print(graphData.getGraphJSON())
