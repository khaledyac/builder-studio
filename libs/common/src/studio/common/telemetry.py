"""OpenTelemetry tracing setup for services.

Spans go to an OTLP/HTTP collector when `OTEL_EXPORTER_OTLP_ENDPOINT` is set, and nowhere
otherwise, so local runs and tests need no collector.
"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from studio.common.health import HEALTH_PATH
from studio.common.settings import ServiceSettings


def otlp_traces_url(endpoint: str) -> str:
    """The OTLP/HTTP traces URL for a collector's base endpoint."""
    return f"{endpoint.rstrip('/')}/v1/traces"


def build_tracer_provider(settings: ServiceSettings) -> TracerProvider:
    """A tracer provider that names the service and its environment on every span."""
    resource = Resource.create(
        {"service.name": settings.service_name, "deployment.environment.name": settings.env}
    )
    provider = TracerProvider(resource=resource)
    if settings.otlp_endpoint is not None:
        exporter = OTLPSpanExporter(endpoint=otlp_traces_url(str(settings.otlp_endpoint)))
        provider.add_span_processor(BatchSpanProcessor(exporter))
    return provider


def instrument_app(app: FastAPI, provider: TracerProvider) -> None:
    """Trace every request to `app`, except the service's own health check."""
    # OpenTelemetry matches this against the full URL (scheme, host and path, no query),
    # so anchor it to the root path: /apps/health is still traced.
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=provider, excluded_urls=f"^https?://[^/]+{HEALTH_PATH}$"
    )


def configure_tracing(settings: ServiceSettings, app: FastAPI | None = None) -> TracerProvider:
    """Set up tracing for the process, and for `app` when given. Call once at startup."""
    provider = build_tracer_provider(settings)
    trace.set_tracer_provider(provider)
    if app is not None:
        instrument_app(app, provider)
    return provider
