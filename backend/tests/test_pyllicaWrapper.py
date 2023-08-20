import pytest
import www.pyllicaWrapper as pyllicaWrapper
from www.models import Ticket


def test_pyllicaWrapper():
    terms = ["la guerre", "la guerre mondiale", "trésor"]
    for term in terms:
        records = pyllicaWrapper.get(
            args=Ticket(
                terms=[term],
                start_date=1900,
                end_date=2000,
            ),
            on_no_records_found=lambda: None,
        )
        if records is None:
            pytest.fail("Pyllica returned None for term: " + term)
        assert all([type(record.count) == float for record in records])
