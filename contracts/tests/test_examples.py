"""Every contract has valid and invalid examples, and each one behaves as labelled.

Examples live in `contracts/examples/<contract>/{valid,invalid}/`, as YAML or JSON. An invalid
example is named `<field>.<what's wrong>`, and it must fail on that field, not on a typo elsewhere.
"""

import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from studio.contracts.catalog import CONTRACTS

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def examples(label: str) -> list[Path]:
    return sorted(p for p in EXAMPLES.rglob("*") if p.is_file() and p.parent.name == label)


def contract_of(path: Path) -> str:
    return path.parent.parent.relative_to(EXAMPLES).as_posix()


def load(path: Path) -> object:
    text = path.read_text()
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


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
    CONTRACTS[contract_of(path)].validate_python(load(path))


@pytest.mark.parametrize("path", examples("invalid"), ids=lambda p: str(p.relative_to(EXAMPLES)))
def test_invalid_example_fails_on_its_field(path: Path) -> None:
    field = path.name.split(".", 1)[0]

    with pytest.raises(ValidationError) as caught:
        CONTRACTS[contract_of(path)].validate_python(load(path))

    failing = [error["loc"] for error in caught.value.errors()]
    assert any(field in loc for loc in failing), f"expected an error on {field!r}: {failing}"
