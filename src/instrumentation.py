"""HTTP instrumentation using prometheus_client, exposed as JSON."""

import time
from collections import deque

from prometheus_client import CollectorRegistry, Counter


class HttpMetrics:
    """Counts requests and derives requests-per-second from process uptime."""

    def __init__(self, window_seconds=60.0):
        self.registry = CollectorRegistry()
        self.requests_total = Counter(
            "http_requests",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )
        self.started_at = time.monotonic()
        self.window_seconds = window_seconds
        self._recent = deque()

    def record(self, method, endpoint, status):
        self.requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status),
        ).inc()
        now = time.monotonic()
        self._recent.append(now)
        self._prune(now)

    def _prune(self, now):
        cutoff = now - self.window_seconds
        while self._recent and self._recent[0] < cutoff:
            self._recent.popleft()

    def snapshot(self):
        now = time.monotonic()
        self._prune(now)
        uptime = max(now - self.started_at, 1e-9)
        total = 0
        by_status = {}
        for metric in self.registry.collect():
            for sample in metric.samples:
                if sample.name != "http_requests_total":
                    continue
                total += sample.value
                status = sample.labels.get("status", "unknown")
                by_status[status] = by_status.get(status, 0) + sample.value
        recent = len(self._recent)
        return {
            "requests_total": int(total),
            "requests_per_second": round(total / uptime, 4),
            "recent_requests_per_second": round(recent / self.window_seconds, 4),
            "window_seconds": self.window_seconds,
            "uptime_seconds": round(uptime, 3),
            "requests_by_status": {key: int(value) for key, value in sorted(by_status.items())},
        }


def register_metrics(application):
    metrics = HttpMetrics()
    application.extensions["http_metrics"] = metrics

    @application.after_request
    def _record_request(response):
        from flask import request

        endpoint = request.endpoint or request.path
        metrics.record(request.method, endpoint, response.status_code)
        return response

    return metrics
