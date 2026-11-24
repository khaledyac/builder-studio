import tomllib
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from studio.contracts.version import CONTRACT_VERSION, CURRENT_MAJOR, ContractVersion

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


class Document(BaseModel):
    contract_version: ContractVersion


def test_version_comes_from_the_package() -> None:
    declared = tomllib.loads(PYPROJECT.read_text())["project"]["version"]

    assert declared == CONTRACT_VERSION


@pytest.mark.parametrize(
    "version", [f"{CURRENT_MAJOR}.0.0", f"{CURRENT_MAJOR}.4.2", f"{CURRENT_MAJOR}.10.0"]
)
def test_same_major_is_accepted(version: str) -> None:
    assert Document(contract_version=version).contract_version == version


def test_another_major_is_rejected_with_a_clear_error() -> None:
    with pytest.raises(ValidationError, match=rf"understands contracts {CURRENT_MAJOR}\.x"):
        Document(contract_version=f"{CURRENT_MAJOR + 1}.0.0")


@pytest.mark.parametrize("version", ["1", "1.0", "v1.0.0", "1.0.0-beta", "01.0.0", ""])
def test_malformed_versions_are_rejected(version: str) -> None:
    with pytest.raises(ValidationError):
        Document(contract_version=version)
