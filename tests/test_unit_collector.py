"""Unit tests for NASA/JPL payload parsing. No network, no database."""

from datetime import datetime

from src.collector import parse_fireballs, parse_sentry

FIREBALL_PAYLOAD = {
    "count": 2,
    "fields": ["date", "lat", "lat-dir", "lon", "lon-dir", "alt", "energy", "impact-e"],
    "data": [
        ["2015-10-13 12:23:08", "8.0", "S", "52.5", "W", None, "2.3", "0.082"],
        ["2015-10-11 00:07:46", "55.4", "N", "18.8", "E", "30.1", "3.0", "0.1"],
    ],
}

SENTRY_PAYLOAD = {
    "count": 2,
    "data": [
        {
            "des": "1979 XB",
            "fullname": "(1979 XB)",
            "ip": "8.89646e-07",
            "ps_cum": "-2.75",
            "ts_max": "0",
            "range": "2056-2113",
            "diameter": "0.66",
        },
        {
            "des": "1994 GK",
            "fullname": "(1994 GK)",
            "ip": "6.9957638e-05",
            "ps_cum": "-3.61",
            "ts_max": "0",
            "range": "2050-2067",
            "diameter": "0.048",
        },
    ],
}


def test_parse_fireballs_maps_fields_and_signed_coordinates():
    rows = parse_fireballs(FIREBALL_PAYLOAD)

    assert len(rows) == 2
    south_west = rows[0]
    assert south_west["occurred_at"] == datetime(2015, 10, 13, 12, 23, 8)
    assert south_west["latitude"] == -8.0
    assert south_west["longitude"] == -52.5
    assert south_west["altitude_km"] is None
    assert south_west["impact_energy_kt"] == 0.082

    north_east = rows[1]
    assert north_east["latitude"] == 55.4
    assert north_east["longitude"] == 18.8
    assert north_east["altitude_km"] == 30.1


def test_parse_sentry_maps_probability_and_scales():
    rows = parse_sentry(SENTRY_PAYLOAD)

    assert [row["designation"] for row in rows] == ["1979 XB", "1994 GK"]
    assert rows[0]["impact_probability"] == 8.89646e-07
    assert rows[0]["palermo_scale"] == -2.75
    assert rows[0]["year_range"] == "2056-2113"


def test_parse_empty_payloads():
    assert parse_fireballs({"count": 0, "fields": ["date"], "data": []}) == []
    assert parse_sentry({"count": 0, "data": []}) == []
