"""`need.yml`: what the builder wants, as the intake understood it."""

from typing import Annotated

from pydantic import Field, StringConstraints

from studio.contracts.common import (
    AccessMode,
    Audience,
    ConnectorId,
    ConnectorIds,
    Contract,
    DomainId,
    ProjectType,
)
from studio.contracts.version import ContractVersion

type Sentence = Annotated[str, StringConstraints(min_length=1, max_length=500)]


class Need(Contract):
    contract_version: ContractVersion
    problem: Annotated[str, StringConstraints(min_length=1, max_length=2000)]
    users: Sentence
    examples: Annotated[list[Sentence], Field(min_length=2, max_length=3)]
    data: ConnectorIds = Field(default_factory=list[ConnectorId])
    """The connectors the app reads or writes."""
    access: AccessMode
    audience: Audience
    out_of_scope: list[Sentence] = Field(default_factory=list[Sentence])
    domain: DomainId
    project_type: ProjectType
