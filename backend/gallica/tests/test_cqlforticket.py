from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from gallica.cqlforticket import CQLforTicket


class TestCQLforTicket(TestCase):
    
    def setUp(self) -> None:
        cqlStringBuilder = CQLforTicket()
        
