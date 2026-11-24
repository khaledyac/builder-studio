import pytest
from pydantic import ValidationError

from studio.common.settings import ServiceSettings


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("SERVICE_NAME", "ENV", "LOG_LEVEL", "OTEL_EXPORTER_OTLP_ENDPOINT", "DATASET"):
        monkeypatch.delenv(name, raising=False)


def test_defaults_suit_local_development() -> None:
    settings = ServiceSettings(service_name="platform-api")

    assert settings.env == "local"
    assert settings.log_level == "INFO"
    assert settings.otlp_endpoint is None


def test_values_come_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SERVICE_NAME", "session-manager")
    monkeypatch.setenv("ENV", "dev")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")

    settings = ServiceSettings()  # pyright: ignore[reportCallIssue]

    assert settings.service_name == "session-manager"
    assert settings.env == "dev"
    assert settings.log_level == "DEBUG"
    assert str(settings.otlp_endpoint) == "http://collector:4318/"


def test_unknown_environment_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "staging")

    with pytest.raises(ValidationError):
        ServiceSettings(service_name="platform-api")


def test_service_name_is_required() -> None:
    with pytest.raises(ValidationError):
        ServiceSettings()  # pyright: ignore[reportCallIssue]


def test_settings_are_immutable() -> None:
    settings = ServiceSettings(service_name="platform-api")

    with pytest.raises(ValidationError):
        settings.env = "prod"  # pyright: ignore[reportAttributeAccessIssue]


def test_services_extend_the_base_class(monkeypatch: pytest.MonkeyPatch) -> None:
    class RegistrySettings(ServiceSettings):
        service_name: str = "registry-api"
        dataset: str = "registry"

    monkeypatch.setenv("DATASET", "registry_test")

    settings = RegistrySettings()

    assert settings.service_name == "registry-api"
    assert settings.dataset == "registry_test"
    assert settings.env == "local"
