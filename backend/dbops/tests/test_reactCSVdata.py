import unittest
from unittest.mock import patch, MagicMock
from dbops.reactCSVdata import ReactCSVdata


class TestReactCSVdata(unittest.TestCase):

    @patch("scripts.reactCSVdata.PSQLconn")
    def setUp(self, mock_conn):
        mock_conn.return_value = mock_conn
        mock_conn.getConn.return_value = mock_conn
        self.reactCSVdata = ReactCSVdata()

    def test_get_csv_data(self):
        mock_cursor_context = MagicMock(
            execute=MagicMock(),
            fetchall=MagicMock(return_value=[('tests', 'tests.com', '2021', '01', '15')])
        )
        self.reactCSVdata.conn.cursor.return_value.__enter__.return_value = mock_cursor_context
        self.reactCSVdata.getCSVData('tests')

        mock_cursor_context.execute.assert_called_once_with(
            """
            SELECT searchterm, identifier, year, month, day 
            FROM results 
            WHERE ticketid IN %s
            ORDER BY year, month, day
            """,
            ((('tests'),),)
        )
        mock_cursor_context.fetchall.assert_called_once()
        self.assertEqual(
            self.reactCSVdata.csvData,
            [
                ['ngram', 'identifier', 'year', 'month', 'day'],
                ('tests', 'tests.com', '2021', '01', '15')
            ]
        )
        self.assertEqual(
            self.reactCSVdata.csvData,
            [['ngram', 'identifier', 'year', 'month', 'day'],
             ('tests', 'tests.com', '2021', '01', '15')]
        )






if __name__ == '__main__':
    unittest.main()
