"""`app.yaml`: the app's identity, data access and resources, kept in its repo."""

from datetime import date
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from studio.contracts.common import (
    SLUG,
    AccessMode,
    AppId,
    Audience,
    ConnectorId,
    DomainId,
    ProjectType,
    RiskTier,
    StrictContract,
    UserId,
)
from studio.contracts.version import ContractVersion

type ApprovedModule = Literal[
    "firestore", "cloud-sql", "cloud-storage", "pubsub", "cloud-scheduler"
]
"""The approved Terraform modules an app's resources come from."""


class Resource(StrictContract):
    module: ApprovedModule
    name: Annotated[str, StringConstraints(pattern=SLUG, max_length=40)]


class AppManifest(StrictContract):
    contract_version: ContractVersion
    name: AppId
    owner: UserId
    domain: DomainId
    project_type: ProjectType
    connectors: dict[ConnectorId, AccessMode] = Field(default_factory=dict[ConnectorId, AccessMode])
    """Each connector the app uses, with its access mode: one entry per connector."""
    resources: list[Resource] = Field(default_factory=list[Resource])
    audience: Audience
    risk_tier: Annotated[RiskTier | None, Field(json_schema_extra={"readOnly": True})] = None
    """Set by the policy check, never by hand. The builder can't pick a lower tier."""
    expires_on: date
