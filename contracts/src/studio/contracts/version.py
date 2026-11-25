"""The contracts version: one semver for every contract, read from the package metadata.

Stored documents and queued messages carry the version they were written with. A reader accepts
any version with its own major, and rejects another major (ADR 0002).
"""

from importlib.metadata import version
from typing import Annotated

from pydantic import AfterValidator, StringConstraints, WithJsonSchema

CONTRACT_VERSION = version("studio-contracts")

SEMVER_PATTERN = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"

type Semver = Annotated[str, StringConstraints(pattern=SEMVER_PATTERN)]
"""A version like 1.4.2."""


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
    StringConstraints(pattern=SEMVER_PATTERN),
    AfterValidator(_readable),
    # Other languages read the generated schema, so it checks the major too.
    WithJsonSchema(
        {
            "type": "string",
            "pattern": rf"^{CURRENT_MAJOR}\.(0|[1-9]\d*)\.(0|[1-9]\d*)$",
            "description": (
                f"The contracts version it was written with. Readers accept {CURRENT_MAJOR}.x."
            ),
        }
    ),
]
"""The contracts version a payload was written with. Readers accept their own major."""
