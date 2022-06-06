from unittest import TestCase
from gallica.ticketGraphData import TicketGraphData


class TestTicketGraphData(TestCase):
    def test_get_graph_json(self):
        graphData = TicketGraphData(
            '1234',
            averagewindow=0,
            groupby='day'
        )
        print(graphData.getGraphJSON())
