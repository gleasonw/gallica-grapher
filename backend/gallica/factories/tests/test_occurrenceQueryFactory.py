from unittest import TestCase
from unittest.mock import patch, MagicMock
from occurrenceQueryFactory import OccurrenceQueryFactory


class TestOccurrenceQueryFactory(TestCase):

    def setUp(self) -> None:
        self.testFactory = OccurrenceQueryFactory()

        self.testFactory.cql = MagicMock()
        self.testFactory.parser = MagicMock()
        self.testFactory.indexer = MagicMock()
        self.testFactory.queryBatcher = MagicMock()

    def test_build_queries_for_options(self):
        options = {'yada yada'}

        test = self.testFactory.buildQueriesForOptions(options)

        self.testFactory.cql.buildStringsForOptions.assert_called_once_with(options)
        self.testFactory.indexer.buildIndexQueries.assert_called_once_with(
            self.testFactory.cql.buildStringsForOptions.return_value
        )
        self.assertDictEqual(
            test,
            {
                'queries': self.testFactory.queryBatcher.return_value,
                'estimateNumResults': self.testFactory.indexer.totalResults
            }
        )
