from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio.common.health import HEALTH_PATH, health_router


def test_health_reports_ok_with_the_service_name() -> None:
    app = FastAPI()
    app.include_router(health_router("platform-api"))

    response = TestClient(app).get(HEALTH_PATH)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "platform-api"}


def test_health_path_avoids_cloud_run_reserved_paths() -> None:
    # Cloud Run reserves URL paths that end in "z", such as /healthz.
    assert HEALTH_PATH == "/health"
