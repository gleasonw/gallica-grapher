from unittest import TestCase
from averageResponseTime import AverageResponseTime


class TestAverageResponseTime(TestCase):

    def setUp(self) -> None:
        self.responseTime = AverageResponseTime()

    def test_update(self):
        self.assertEqual(self.responseTime.update(1), 1)
        self.assertEqual(self.responseTime.update(5), 3)