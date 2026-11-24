from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from studio.common.health import health_router
from studio.common.settings import ServiceSettings
from studio.common.telemetry import build_tracer_provider, instrument_app, otlp_traces_url


def capture(provider: TracerProvider) -> InMemorySpanExporter:
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return exporter


def test_spans_carry_the_service_name_and_environment() -> None:
    provider = build_tracer_provider(ServiceSettings(service_name="platform-api", env="dev"))
    exporter = capture(provider)

    with provider.get_tracer("test").start_as_current_span("work"):
        pass

    (span,) = exporter.get_finished_spans()
    assert span.resource.attributes["service.name"] == "platform-api"
    assert span.resource.attributes["deployment.environment.name"] == "dev"


def test_otlp_traces_url_appends_the_traces_path() -> None:
    assert otlp_traces_url("http://collector:4318/") == "http://collector:4318/v1/traces"
    assert otlp_traces_url("http://collector:4318") == "http://collector:4318/v1/traces"


def test_instrumented_app_traces_requests_but_not_health_checks() -> None:
    provider = build_tracer_provider(ServiceSettings(service_name="platform-api"))
    exporter = capture(provider)
    app = FastAPI()
    app.include_router(health_router("platform-api"))

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"pong": "yes"}

    instrument_app(app, provider)
    client = TestClient(app)
    client.get("/health")
    assert exporter.get_finished_spans() == ()

    client.get("/ping")
    server_spans = [s for s in exporter.get_finished_spans() if s.name == "GET /ping"]
    assert len(server_spans) == 1
    assert server_spans[0].resource.attributes["service.name"] == "platform-api"
