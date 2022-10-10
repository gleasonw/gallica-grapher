import unittest
from gallica.factories.ticketQueryFactory import TicketQueryFactory
from unittest.mock import MagicMock
from gallica.fetchComponents.query import Query


class TestTicketQueryFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.testTicketQueryFactory = TicketQueryFactory()

    def test_buildWithCodeBundles(self):
        testTicket = MagicMock(
            getCodeBundles=MagicMock(return_value=[['code1', 'code2']]),
            getTerms=MagicMock(return_value=['term1', 'term2']),
        )
        startEndDates = [['start1', 'end1'], ['start2', 'end2']]

        test = self.testTicketQueryFactory.build(
            ticket=testTicket,
            startEndDates=startEndDates
        )

        self.assertEqual(len(test), 4)

    def test_buildNoCodeBundles(self):
        testTicket = MagicMock(
            getCodeBundles=MagicMock(return_value=[]),
            getTerms=MagicMock(return_value=['term1', 'term2']),
        )
        startEndDates = [['start1', 'end1'], ['start2', 'end2']]

        test = self.testTicketQueryFactory.build(
            ticket=testTicket,
            startEndDates=startEndDates
        )

        self.assertEqual(len(test), 4)


if __name__ == '__main__':
    unittest.main()
