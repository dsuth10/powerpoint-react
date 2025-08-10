from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

def setup_metrics(app: FastAPI):
    # Expose Prometheus metrics under text/plain; align OpenAPI for contract tests
    # Ensure the metrics endpoint itself is included in instrumentation so histograms have _count samples
    Instrumentator(excluded_handlers=[]).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=True,
        response_class=PlainTextResponse,
    )