"""The settings every service shares. Each service subclasses `ServiceSettings`."""

from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

type Environment = Literal["local", "dev", "prod"]
type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ServiceSettings(BaseSettings):
    """Read from environment variables (`SERVICE_NAME`, `ENV`, `LOG_LEVEL`, ...).

    Secrets never live here: services read them from Secret Manager.
    """

    model_config = SettingsConfigDict(frozen=True, extra="ignore", validate_by_name=True)

    service_name: str
    env: Environment = "local"
    log_level: LogLevel = "INFO"
    # The standard OpenTelemetry variable, so collectors and SDK docs line up.
    otlp_endpoint: AnyHttpUrl | None = Field(
        default=None, validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
