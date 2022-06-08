from unittest import TestCase
from gallica.ticketGraphOptions import TicketGraphOptions


class TestTicketGraphSeries(TestCase):
    def test_get_graph_json(self):
        graphData = TicketGraphOptions(
            '1234',
            averagewindow=0,
            groupby='year'
        )
        print(graphData.getGraphJSON())
