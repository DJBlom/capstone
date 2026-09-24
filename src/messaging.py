"""RabbitMQ helpers for event collaboration (Pika).

The collector is the producer. The consumer process subscribes through the
broker. If the broker is down, producers log and continue — the SQL store is
still the source of truth.
"""

from __future__ import annotations

import json
import logging
import os
import uuid

import pika

QUEUE_COLLECTION = "collection.completed"
QUEUE_ANALYSIS = "analysis.completed"

logger = logging.getLogger(__name__)


def broker_host():
    return os.environ.get("RABBITMQ_HOST", "localhost")


def connect(host=None):
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=host or broker_host())
    )


def publish_event(queue, body, channel=None):
    payload = dict(body)
    payload.setdefault("correlation_id", str(uuid.uuid4()))
    encoded = json.dumps(payload)
    owns_connection = channel is None
    connection = None
    if channel is None:
        connection = connect()
        channel = connection.channel()
    try:
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=encoded,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )
    finally:
        if owns_connection and connection is not None:
            connection.close()
    return payload


def start_consumer(queue, on_message, host=None):
    connection = connect(host=host)
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        on_message(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue, on_message_callback=callback)
    logger.info("waiting for messages on %s", queue)
    channel.start_consuming()
