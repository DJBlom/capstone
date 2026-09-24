"""Unit and integration tests for event collaboration (no live RabbitMQ)."""

from src.consumer import analyze_collection_event
from src.messaging import QUEUE_ANALYSIS, QUEUE_COLLECTION, publish_event


class FakeChannel:
    def __init__(self):
        self.declared = []
        self.published = []

    def queue_declare(self, queue, durable=False):
        self.declared.append((queue, durable))

    def basic_publish(self, exchange, routing_key, body, properties=None):
        self.published.append(
            {
                "exchange": exchange,
                "routing_key": routing_key,
                "body": body,
                "properties": properties,
            }
        )


def test_publish_event_declares_queue_and_sends_json():
    channel = FakeChannel()
    payload = publish_event(
        QUEUE_COLLECTION,
        {"event_type": "collection.completed", "fireballs": 3},
        channel=channel,
    )
    assert payload["fireballs"] == 3
    assert "correlation_id" in payload
    assert channel.declared == [(QUEUE_COLLECTION, True)]
    assert channel.published[0]["routing_key"] == QUEUE_COLLECTION
    assert channel.published[0]["exchange"] == ""


def test_consumer_emits_analysis_completed(app):
    published = []

    def capture(queue, body):
        published.append((queue, body))
        return body

    result = analyze_collection_event(
        {
            "event_type": "collection.completed",
            "correlation_id": "abc-123",
            "fireballs": 2,
            "sentry": 2,
        },
        app,
        publish=capture,
    )
    assert result["event_type"] == "analysis.completed"
    assert result["correlation_id"] == "abc-123"
    assert published[0][0] == QUEUE_ANALYSIS
    assert "fireballs" in result["summary"]
