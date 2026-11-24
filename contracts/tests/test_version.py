import tomllib
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from studio.contracts.version import CONTRACT_VERSION, ContractVersion

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


class Document(BaseModel):
    contract_version: ContractVersion


def test_version_comes_from_the_package() -> None:
    declared = tomllib.loads(PYPROJECT.read_text())["project"]["version"]

    assert declared == CONTRACT_VERSION


@pytest.mark.parametrize("version", ["1.0.0", "1.4.2", "1.10.0"])
def test_same_major_is_accepted(version: str) -> None:
    assert Document(contract_version=version).contract_version == version


def test_another_major_is_rejected_with_a_clear_error() -> None:
    with pytest.raises(ValidationError, match=r"understands contracts 1\.x"):
        Document(contract_version="2.0.0")


@pytest.mark.parametrize("version", ["1", "1.0", "v1.0.0", "1.0.0-beta", "01.0.0", ""])
def test_malformed_versions_are_rejected(version: str) -> None:
    with pytest.raises(ValidationError):
        Document(contract_version=version)
