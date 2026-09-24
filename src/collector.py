#!/usr/bin/env python3
"""Separate data-collection process for Impact Sentinel.

Fetches current fireballs and future Sentry risk from NASA/JPL REST APIs
and upserts them into the same SQL store the web app reads.

Run from the project root:

    python -m src.collector

Schedule with cron (hourly) or Heroku Scheduler.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

import requests

from src.app import create_app
from src.messaging import QUEUE_COLLECTION, publish_event
from src.models import FireballEvent, SentryObject, db

FIREBALL_URL = "https://ssd-api.jpl.nasa.gov/fireball.api"
SENTRY_URL = "https://ssd-api.jpl.nasa.gov/sentry.api"
USER_AGENT = "ImpactSentinel/0.1 (CU Boulder capstone; educational)"

logger = logging.getLogger(__name__)


def fetch_json(url, params=None, http_get=requests.get):
    response = http_get(
        url,
        params=params,
        timeout=30,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()


def _signed_degrees(magnitude, direction):
    if magnitude is None or magnitude == "":
        return None
    value = float(magnitude)
    if direction in {"S", "W"}:
        return -value
    return value


def _as_float(value):
    if value is None or value == "":
        return None
    return float(value)


def _as_int(value):
    if value is None or value == "":
        return None
    return int(float(value))


def parse_fireballs(payload):
    fields = payload.get("fields") or []
    rows = []
    for raw in payload.get("data") or []:
        record = dict(zip(fields, raw))
        # API timestamps are GMT; store naive UTC so SQLite unique keys match.
        occurred = datetime.strptime(record["date"], "%Y-%m-%d %H:%M:%S")
        rows.append(
            {
                "occurred_at": occurred,
                "latitude": _signed_degrees(record.get("lat"), record.get("lat-dir")),
                "longitude": _signed_degrees(record.get("lon"), record.get("lon-dir")),
                "altitude_km": _as_float(record.get("alt")),
                "radiated_energy": _as_float(record.get("energy")),
                "impact_energy_kt": _as_float(record.get("impact-e")),
            }
        )
    return rows


def parse_sentry(payload):
    rows = []
    for record in payload.get("data") or []:
        rows.append(
            {
                "designation": record["des"],
                "fullname": record.get("fullname"),
                "impact_probability": _as_float(record.get("ip")),
                "palermo_scale": _as_float(record.get("ps_cum")),
                "torino_scale": _as_int(record.get("ts_max")),
                "year_range": record.get("range"),
                "diameter_km": _as_float(record.get("diameter")),
            }
        )
    return rows


def _upsert_fireball(row, collected_at):
    existing = FireballEvent.query.filter_by(occurred_at=row["occurred_at"]).one_or_none()
    if existing is None:
        existing = FireballEvent(occurred_at=row["occurred_at"])
        db.session.add(existing)
    existing.latitude = row["latitude"]
    existing.longitude = row["longitude"]
    existing.altitude_km = row["altitude_km"]
    existing.radiated_energy = row["radiated_energy"]
    existing.impact_energy_kt = row["impact_energy_kt"]
    existing.collected_at = collected_at


def _upsert_sentry(row, collected_at):
    existing = SentryObject.query.filter_by(designation=row["designation"]).one_or_none()
    if existing is None:
        existing = SentryObject(designation=row["designation"])
        db.session.add(existing)
    existing.fullname = row["fullname"]
    existing.impact_probability = row["impact_probability"]
    existing.palermo_scale = row["palermo_scale"]
    existing.torino_scale = row["torino_scale"]
    existing.year_range = row["year_range"]
    existing.diameter_km = row["diameter_km"]
    existing.collected_at = collected_at


def run_collection(app, http_get=requests.get, publish=publish_event):
    """Fetch NASA/JPL catalogs and persist them. Returns counts written."""
    collected_at = datetime.now(timezone.utc)
    with app.app_context():
        fireball_payload = fetch_json(
            FIREBALL_URL,
            params={"limit": 20},
            http_get=http_get,
        )
        sentry_payload = fetch_json(SENTRY_URL, http_get=http_get)

        fireballs = parse_fireballs(fireball_payload)
        sentry_objects = parse_sentry(sentry_payload)

        for row in fireballs:
            _upsert_fireball(row, collected_at)
        for row in sentry_objects:
            _upsert_sentry(row, collected_at)

        db.session.commit()
        stats = {"fireballs": len(fireballs), "sentry": len(sentry_objects)}
        logger.info("collection complete: %s", stats)
        event = {
            "event_type": "collection.completed",
            "correlation_id": str(uuid4()),
            "fireballs": stats["fireballs"],
            "sentry": stats["sentry"],
            "collected_at": collected_at.isoformat(),
        }
        try:
            publish(QUEUE_COLLECTION, event)
        except Exception:
            logger.exception(
                "message broker unavailable; catalog already stored in SQL"
            )
        return stats


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    app = create_app()
    stats = run_collection(app)
    print(f"Stored {stats['fireballs']} fireballs and {stats['sentry']} sentry objects.")


if __name__ == "__main__":
    main()
