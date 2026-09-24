#!/usr/bin/env python3
"""Message consumer: subscribe to collection.completed and run analysis.

    python -m src.consumer
"""

from __future__ import annotations

import logging
import os
import sys

from src.analyzer import catalog_summary
from src.app import create_app
from src.messaging import QUEUE_ANALYSIS, QUEUE_COLLECTION, publish_event, start_consumer

logger = logging.getLogger(__name__)


def analyze_collection_event(message, app, publish=publish_event):
    """React to a collection event: analyze stored rows, emit analysis.completed."""
    with app.app_context():
        summary = catalog_summary()
        event = {
            "event_type": "analysis.completed",
            "correlation_id": message.get("correlation_id"),
            "collection": {
                "fireballs": message.get("fireballs"),
                "sentry": message.get("sentry"),
            },
            "summary": summary,
        }
        publish(QUEUE_ANALYSIS, event)
        logger.info(
            "analyzed collection %s: %s fireballs, %s sentry objects",
            message.get("correlation_id"),
            summary["fireballs"]["count"],
            summary["sentry"]["count"],
        )
        return event


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    app = create_app()

    def on_message(message):
        logger.info("received %s", message)
        analyze_collection_event(message, app)

    print("[*] Waiting for collection.completed. To exit press CTRL+C")
    start_consumer(QUEUE_COLLECTION, on_message)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
