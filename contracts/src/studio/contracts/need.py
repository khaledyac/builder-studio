"""`need.yml`: what the builder wants, as the intake understood it."""

from typing import Annotated

from pydantic import Field, StringConstraints

from studio.contracts.common import (
    AccessMode,
    Audience,
    ConnectorId,
    ConnectorIds,
    DomainId,
    Line,
    ProjectType,
    StrictContract,
)
from studio.contracts.version import ContractVersion


class Need(StrictContract):
    contract_version: ContractVersion
    problem: Annotated[str, StringConstraints(min_length=1, max_length=2000)]
    users: Line
    examples: Annotated[list[Line], Field(min_length=2, max_length=3)]
    data: ConnectorIds = Field(default_factory=list[ConnectorId])
    """The connectors the app reads or writes."""
    access: AccessMode
    audience: Audience
    out_of_scope: list[Line] = Field(default_factory=list[Line])
    domain: DomainId
    project_type: ProjectType
