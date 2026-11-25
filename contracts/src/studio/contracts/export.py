"""Write the generated contract files from the Pydantic models.

    python -m studio.contracts.export contracts/generated

writes `schemas/` (one JSON Schema per contract), `events/` (one per event type) and
`workspace-api/openapi.json`. `task contracts-gen` then adds the TypeScript types.
"""

import json
import sys
from pathlib import Path
from typing import Any

from pydantic.json_schema import GenerateJsonSchema

from studio.contracts.catalog import SCHEMAS
from studio.contracts.events import EVENTS
from studio.contracts.version import CONTRACT_VERSION
from studio.contracts.workspace_api import openapi

STAMP = (
    f"Builder Studio contracts {CONTRACT_VERSION}. Generated from studio.contracts: "
    "edit the Pydantic models, then run task contracts-gen."
)
TS_BANNER = f"/* {STAMP} */"
"""The banner `task contracts-gen` puts on the generated TypeScript files."""


class _WithoutFieldTitles(GenerateJsonSchema):
    """Models and named types keep their titles. Field titles would only add noise, such as one
    TypeScript alias per field."""

    def field_title_should_be_set(self, schema: Any) -> bool:  # noqa: ANN401 (its type is private)
        return False


def _title(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("-"))


def _schema(schema: dict[str, Any], title: str) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$comment": STAMP,
        "title": schema.get("title", title),
        **{key: value for key, value in schema.items() if key != "title"},
    }


def _write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")


def export(out: Path) -> None:
    """Write every generated contract file under `out`."""
    for name, adapter in SCHEMAS.items():
        _write(
            out / "schemas" / f"{name}.schema.json",
            _schema(adapter.json_schema(schema_generator=_WithoutFieldTitles), _title(name)),
        )
    for event_type, model in EVENTS.items():
        _write(
            out / "events" / f"{event_type}.schema.json",
            _schema(model.model_json_schema(schema_generator=_WithoutFieldTitles), model.__name__),
        )
    _write(out / "workspace-api" / "openapi.json", openapi())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m studio.contracts.export <output directory>")
    export(Path(sys.argv[1]))
