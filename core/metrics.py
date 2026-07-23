"""Prometheus metrics for the AI Proxy system."""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['endpoint']
)


def metrics_data() -> bytes:
    """Return Prometheus metrics in text format."""
    return generate_latest()


def metrics_content_type() -> str:
    """Return the content type for Prometheus metrics."""
    return CONTENT_TYPE_LATEST
