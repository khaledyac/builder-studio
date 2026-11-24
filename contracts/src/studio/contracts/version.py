"""The contracts version: one semver for every contract, read from the package metadata.

Stored documents and queued messages carry the version they were written with. A reader accepts
any version with its own major, and rejects another major (ADR 0002).
"""

from importlib.metadata import version
from typing import Annotated

from pydantic import AfterValidator, StringConstraints

CONTRACT_VERSION = version("studio-contracts")

_SEMVER = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"


def major(semver: str) -> int:
    """The major part of a version like 1.4.2."""
    return int(semver.split(".", 1)[0])


CURRENT_MAJOR = major(CONTRACT_VERSION)


def _readable(value: str) -> str:
    if major(value) != CURRENT_MAJOR:
        raise ValueError(
            f"written with contracts {value}, but this reader understands contracts "
            f"{CURRENT_MAJOR}.x: migrate it first (ADR 0002)"
        )
    return value


ContractVersion = Annotated[
    str,
    StringConstraints(pattern=_SEMVER),
    AfterValidator(_readable),
]
"""The contracts version a payload was written with. Readers accept their own major."""
