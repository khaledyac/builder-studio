import json
from pathlib import Path

from studio.contracts.catalog import SCHEMAS
from studio.contracts.events import EVENTS
from studio.contracts.export import export
from studio.contracts.version import CONTRACT_VERSION


def files(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_export_writes_every_schema_event_and_the_openapi(tmp_path: Path) -> None:
    export(tmp_path)

    written = set(files(tmp_path))
    assert {f"schemas/{name}.schema.json" for name in SCHEMAS} <= written
    assert {f"events/{event_type}.schema.json" for event_type in EVENTS} <= written
    assert "workspace-api/openapi.json" in written


def test_every_generated_file_carries_the_contracts_version(tmp_path: Path) -> None:
    export(tmp_path)

    for path in [*tmp_path.glob("schemas/*.json"), *tmp_path.glob("events/*.json")]:
        assert CONTRACT_VERSION in json.loads(path.read_text())["$comment"], path.name
    openapi = json.loads((tmp_path / "workspace-api/openapi.json").read_text())
    assert openapi["info"]["version"] == CONTRACT_VERSION


def test_export_is_deterministic(tmp_path: Path) -> None:
    export(tmp_path / "first")
    export(tmp_path / "second")

    assert files(tmp_path / "first") == files(tmp_path / "second")
