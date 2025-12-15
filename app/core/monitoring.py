# app/core/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Sentry para error tracking
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1  # 10% de traces
)

# Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

# Custom metrics
from prometheus_client import Counter, Histogram

generation_requests = Counter(
    "generation_requests_total",
    "Total generation requests",
    ["prompt_name", "status"]
)

generation_latency = Histogram(
    "generation_latency_seconds",
    "Generation latency",
    ["prompt_name"]
)