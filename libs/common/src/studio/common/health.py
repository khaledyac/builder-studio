"""The health endpoint every service exposes."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

# Not /healthz: Cloud Run reserves URL paths that end in "z".
HEALTH_PATH = "/health"


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"
    service: str


def health_router(service_name: str) -> APIRouter:
    """A router serving `GET /health` for the named service."""
    router = APIRouter(tags=["health"])

    @router.get(HEALTH_PATH)
    def health() -> HealthStatus:  # pyright: ignore[reportUnusedFunction]
        return HealthStatus(service=service_name)

    return router
