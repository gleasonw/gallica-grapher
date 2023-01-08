from unittest import TestCase
from unittest.mock import MagicMock
from gallicaGetter.searchArgs import SearchArgs
import search as search


class Test(TestCase):
    def test_all_volume_occurrence_search(self):
        # given
        args = SearchArgs(
            terms=["test"],
            start_date="1860",
            end_date="1880",
            codes=["test"],
            grouping="all",
        )
        search.insert_records_into_db = MagicMock()
        # when
        search.get_and_insert_records_for_args(
            ticketID="test",
            requestID="test",
            args=args,
            onProgressUpdate=MagicMock(),
            conn=MagicMock(),
            api=MagicMock(),
        )
        # then
        search.insert_records_into_db.assert_called_once()

    def test_period_occurrence_search(self):
        # given
        args = SearchArgs(
            terms=["test"],
            start_date="1860",
            end_date="1880",
            codes=["test"],
            grouping="year",
        )
        search.insert_records_into_db = MagicMock()
        # when
        search.get_and_insert_records_for_args(
            ticketID="test",
            requestID="test",
            args=args,
            onProgressUpdate=MagicMock(),
            conn=MagicMock(),
            api=MagicMock(),
        )
        # then
        search.insert_records_into_db.assert_called_once()

    def test_pyllica_search(self):
        # given
        args = SearchArgs(
            terms=["test"],
            start_date="1860",
            end_date="1880",
            grouping="year",
        )
        search.insert_records_into_db = MagicMock()
        search.pyllicaWrapper = MagicMock()
        # when
        search.get_and_insert_records_for_args(
            ticketID="test",
            requestID="test",
            args=args,
            onProgressUpdate=MagicMock(),
            conn=MagicMock(),
        )
        # then
        search.insert_records_into_db.assert_called_once()
