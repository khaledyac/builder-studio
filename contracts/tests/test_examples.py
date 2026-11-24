"""Every contract has valid and invalid examples, and each one behaves as labelled, both in the
Pydantic models and in the generated JSON Schema or OpenAPI that other languages use.

Examples live in `contracts/examples/<contract>/{valid,invalid}/`, as YAML or JSON. An invalid
example is named `<field>.<what's wrong>`, and every error it raises must be on that field, so a
typo elsewhere can't make it pass for the wrong reason.
"""

import json
from collections.abc import Mapping
from functools import cache
from pathlib import Path
from typing import Any, cast

import pytest
import yaml
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from studio.contracts.catalog import CONTRACTS

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
GENERATED = ROOT / "generated"

type Json = dict[str, Json] | list[Json] | str | int | float | bool | None
type Schema = Mapping[str, Any] | bool


def examples(label: str) -> list[Path]:
    return sorted(p for p in EXAMPLES.rglob("*") if p.is_file() and p.parent.name == label)


def contract_of(path: Path) -> str:
    return path.parent.parent.relative_to(EXAMPLES).as_posix()


def load(path: Path) -> Json:
    text = path.read_text()
    data: object = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    # YAML reads dates as dates; the wire format is JSON, so compare in JSON terms.
    return cast(Json, json.loads(json.dumps(data, default=str)))


@cache
def generated_validator(contract: str) -> Draft202012Validator:
    """The validator another language would use: the generated schema or OpenAPI component."""
    checker = Draft202012Validator.FORMAT_CHECKER
    if not contract.startswith("workspace-api/"):
        schema = json.loads((GENERATED / "schemas" / f"{contract}.schema.json").read_text())
        return Draft202012Validator(schema, format_checker=checker)
    openapi = json.loads((GENERATED / "workspace-api" / "openapi.json").read_text())
    resource: Resource[Schema] = Resource.from_contents(openapi, default_specification=DRAFT202012)
    registry = Registry[Schema]().with_resource("urn:openapi", resource)
    component = "".join(part.capitalize() for part in contract.split("/")[1].split("-"))
    ref = {"$ref": f"urn:openapi#/components/schemas/{component}"}
    return Draft202012Validator(ref, registry=registry, format_checker=checker)


def test_every_contract_has_valid_and_invalid_examples() -> None:
    valid = {contract_of(p) for p in examples("valid")}
    invalid = {contract_of(p) for p in examples("invalid")}

    assert set(CONTRACTS) <= valid, f"no valid example: {sorted(set(CONTRACTS) - valid)}"
    assert set(CONTRACTS) <= invalid, f"no invalid example: {sorted(set(CONTRACTS) - invalid)}"


def test_every_example_belongs_to_a_contract() -> None:
    folders = {contract_of(p) for p in examples("valid") + examples("invalid")}

    assert folders <= set(CONTRACTS), f"unknown contracts: {sorted(folders - set(CONTRACTS))}"


@pytest.mark.parametrize("path", examples("valid"), ids=lambda p: str(p.relative_to(EXAMPLES)))
def test_valid_example_passes(path: Path) -> None:
    data = load(path)

    CONTRACTS[contract_of(path)].validate_python(data)
    errors = [e.message for e in generated_validator(contract_of(path)).iter_errors(data)]  # pyright: ignore[reportUnknownMemberType]  # untyped overload
    assert errors == [], f"the generated schema rejects it: {errors}"


@pytest.mark.parametrize("path", examples("invalid"), ids=lambda p: str(p.relative_to(EXAMPLES)))
def test_invalid_example_fails_on_its_field(path: Path) -> None:
    field = path.name.split(".", 1)[0]
    data = load(path)

    with pytest.raises(ValidationError) as caught:
        CONTRACTS[contract_of(path)].validate_python(data)

    failing = [error["loc"] for error in caught.value.errors()]
    assert all(field in loc for loc in failing), f"expected errors on {field!r} only: {failing}"
    assert not generated_validator(contract_of(path)).is_valid(data), (  # pyright: ignore[reportUnknownMemberType]  # untyped overload
        "the generated schema accepts it"
    )
