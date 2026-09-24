"""Integration tests for fireball energy analysis over a date range."""

from datetime import datetime

import pytest

from src.models import FireballEvent, db


def _seed_fireballs(app):
    with app.app_context():
        db.session.add(
            FireballEvent(occurred_at=datetime(2024, 1, 1, 12, 0, 0), impact_energy_kt=10.0)
        )
        db.session.add(
            FireballEvent(occurred_at=datetime(2024, 1, 15, 8, 0, 0), impact_energy_kt=20.0)
        )
        db.session.add(
            FireballEvent(occurred_at=datetime(2025, 6, 1, 0, 0, 0), impact_energy_kt=100.0)
        )
        db.session.commit()


def test_average_endpoint_returns_mean_energy_in_range(client, app):
    _seed_fireballs(app)

    response = client.get("/average/2024-01-01/2024-01-31")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 2
    assert payload["average_impact_energy_kt"] == 15.0
    assert payload["max_impact_energy_kt"] == 20.0
    assert payload["total_impact_energy_kt"] == 30.0
    assert payload["start_date"] == "2024-01-01"
    assert payload["end_date"] == "2024-01-31"


def test_average_endpoint_empty_range(client, app):
    _seed_fireballs(app)

    response = client.get("/average/2010-01-01/2010-12-31")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 0
    assert payload["average_impact_energy_kt"] is None


def test_average_endpoint_rejects_inverted_range(client):
    response = client.get("/average/2024-12-31/2024-01-01")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_summary_endpoint_includes_sentry_and_fireballs(client, app):
    _seed_fireballs(app)

    response = client.get("/api/summary")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["fireballs"]["count"] == 3
    assert payload["fireballs"]["average_impact_energy_kt"] == pytest.approx(130.0 / 3)
    assert "sentry" in payload
