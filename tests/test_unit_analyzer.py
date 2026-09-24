"""Unit tests for date-range parsing used by the analyzer."""

import pytest

from src.analyzer import DateRangeError, parse_iso_date


def test_parse_iso_date_accepts_yyyy_mm_dd():
    parsed = parse_iso_date("2024-01-15")
    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 15


@pytest.mark.parametrize("value", ["01-15-2024", "2024/01/15", "yesterday", ""])
def test_parse_iso_date_rejects_bad_values(value):
    with pytest.raises(DateRangeError):
        parse_iso_date(value)
