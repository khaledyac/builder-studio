import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind
from pydantic import BaseModel

from studio.common.health import health_router
from studio.common.settings import ServiceSettings
from studio.common.telemetry import (
    build_tracer_provider,
    configure_tracing,
    instrument_app,
    otlp_traces_url,
)


class Pong(BaseModel):
    pong: bool = True


@pytest.fixture(autouse=True)
def no_collector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)


@pytest.fixture
def collector(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[str]]:
    """A fake OTLP/HTTP collector. Yields the paths it receives spans on."""
    paths: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            paths.append(self.path)
            self.send_response(200)
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    for name in ("NO_PROXY", "no_proxy"):
        monkeypatch.setenv(name, "127.0.0.1")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", f"http://127.0.0.1:{server.server_port}")
    yield paths
    server.shutdown()
    server.server_close()


def capture(provider: TracerProvider) -> InMemorySpanExporter:
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return exporter


def server_spans(exporter: InMemorySpanExporter) -> list[str]:
    return [span.name for span in exporter.get_finished_spans() if span.kind is SpanKind.SERVER]


def demo_app() -> FastAPI:
    app = FastAPI()
    app.include_router(health_router("platform-api"))

    @app.get("/ping")
    def ping() -> Pong:  # pyright: ignore[reportUnusedFunction]
        return Pong()

    @app.get("/apps/health")
    def app_health() -> Pong:  # pyright: ignore[reportUnusedFunction]
        return Pong()

    return app


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


def test_spans_are_exported_to_the_configured_collector(collector: list[str]) -> None:
    provider = build_tracer_provider(ServiceSettings(service_name="platform-api"))

    with provider.get_tracer("test").start_as_current_span("work"):
        pass
    provider.force_flush()
    provider.shutdown()

    assert collector == ["/v1/traces"]


def test_instrumented_app_traces_requests_but_not_its_health_check() -> None:
    provider = build_tracer_provider(ServiceSettings(service_name="platform-api"))
    exporter = capture(provider)
    app = demo_app()
    instrument_app(app, provider)
    client = TestClient(app)

    client.get("/health")
    assert server_spans(exporter) == []

    client.get("/ping")
    client.get("/apps/health")
    assert server_spans(exporter) == ["GET /ping", "GET /apps/health"]


def test_configure_tracing_sets_the_global_provider_and_instruments_the_app() -> None:
    app = demo_app()

    provider = configure_tracing(ServiceSettings(service_name="platform-api"), app)
    exporter = capture(provider)
    TestClient(app).get("/ping")

    assert trace.get_tracer_provider() is provider
    assert server_spans(exporter) == ["GET /ping"]
