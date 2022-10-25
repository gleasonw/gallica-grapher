import unittest
from unittest.mock import MagicMock


class TestQueryBuilder(unittest.TestCase):

    def setUp(self) -> None:
        self.testTicketQueryFactory = TicketQueryFactory()
        self.testTicket = MagicMock(
            getCodeBundles=MagicMock(return_value=[['code1', 'code2']]),
            getTerms=MagicMock(return_value=['term1', 'term2']),
            getDateGroupings=MagicMock(return_value=[
                ('date1', 'date2'),
                ('date3', 'date4')
            ]),
        )

    def test_buildWithCodeBundles(self):
        test = self.testTicketQueryFactory.buildBaseQueriesFromArgs(self.testTicket)

        self.assertEqual(len(test), 4)

    def test_buildNoCodeBundles(self):
        test = self.testTicketQueryFactory.buildBaseQueriesFromArgs(self.testTicket)

        self.assertEqual(len(test), 4)


if __name__ == '__main__':
    unittest.main()
