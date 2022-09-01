from utils.removeOldResultsFromDB import removeOldResultsFromDB
import unittest
from unittest.mock import patch, MagicMock


class TestRemoveOldResultsFromDB(unittest.TestCase):

    @patch('chartUtils.removeOldResultsFromDB.PSQLconn')
    def test_removeOldResultsFromDB(self, mock_conn):
        mock_conn.return_value = mock_conn
        mock_conn.getConn.return_value = mock_conn
        mock_conn.close = MagicMock()
        mock_conn.cursor.return_value = mock_conn
        mock_conn.execute = MagicMock()
        mock_conn.commit = MagicMock()
        deleteQuery = "DELETE FROM results WHERE created < NOW() - INTERVAL '1 hour';"

        removeOldResultsFromDB()

        mock_conn.cursor.assert_called_once()
        mock_conn.execute.assert_called_with(deleteQuery)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
