"""The health endpoint every service exposes. Its body is the contracts' `HealthStatus`."""

from fastapi import APIRouter

from studio.contracts.common import HealthStatus

# Not /healthz: Cloud Run reserves URL paths that end in "z".
HEALTH_PATH = "/health"


def health_router(service_name: str) -> APIRouter:
    """A router serving `GET /health` for the named service."""
    router = APIRouter(tags=["health"])

    @router.get(HEALTH_PATH)
    def health() -> HealthStatus:  # pyright: ignore[reportUnusedFunction]
        return HealthStatus(service=service_name)

    return router
