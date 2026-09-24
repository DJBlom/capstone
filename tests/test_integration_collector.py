"""Integration test: mocked REST responses persist into SQLite via the collector."""

from src.collector import run_collection
from src.messaging import QUEUE_COLLECTION
from src.models import FireballEvent, SentryObject
from tests.test_unit_collector import FIREBALL_PAYLOAD, SENTRY_PAYLOAD


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def fake_get(url, params=None, timeout=None, headers=None):
    if "fireball" in url:
        return FakeResponse(FIREBALL_PAYLOAD)
    if "sentry" in url:
        return FakeResponse(SENTRY_PAYLOAD)
    raise AssertionError(f"unexpected url {url}")


def test_run_collection_upserts_fireballs_and_sentry(app):
    published = []

    def capture(queue, body):
        published.append((queue, body))
        return body

    stats = run_collection(app, http_get=fake_get, publish=capture)
    assert stats == {"fireballs": 2, "sentry": 2}
    assert published[0][0] == QUEUE_COLLECTION
    assert published[0][1]["event_type"] == "collection.completed"
    assert published[0][1]["fireballs"] == 2

    with app.app_context():
        assert FireballEvent.query.count() == 2
        assert SentryObject.query.count() == 2
        boulderish = FireballEvent.query.filter_by(impact_energy_kt=0.082).one()
        assert boulderish.latitude == -8.0
        sentry = SentryObject.query.filter_by(designation="1979 XB").one()
        assert sentry.year_range == "2056-2113"

    again = run_collection(app, http_get=fake_get, publish=capture)
    assert again == {"fireballs": 2, "sentry": 2}
    with app.app_context():
        assert FireballEvent.query.count() == 2
        assert SentryObject.query.count() == 2
