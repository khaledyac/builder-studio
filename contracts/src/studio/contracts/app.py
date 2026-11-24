"""`app.yaml`: the app's identity, data access and resources, kept in its repo."""

from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, StringConstraints

from studio.contracts.common import (
    AccessMode,
    AppId,
    Audience,
    ConnectorId,
    Contract,
    DomainId,
    ProjectType,
    RiskTier,
    UserId,
)
from studio.contracts.version import ContractVersion

type ApprovedModule = Literal[
    "firestore", "cloud-sql", "cloud-storage", "pubsub", "cloud-scheduler"
]
"""The approved Terraform modules an app's resources come from."""


class ConnectorUse(Contract):
    id: ConnectorId
    access: AccessMode


class Resource(Contract):
    module: ApprovedModule
    name: Annotated[str, StringConstraints(pattern=r"^[a-z]([a-z0-9-]*[a-z0-9])?$", max_length=40)]


def _one_use_per_connector(connectors: list[ConnectorUse]) -> list[ConnectorUse]:
    ids = [connector.id for connector in connectors]
    if len(set(ids)) != len(ids):
        raise ValueError("each connector can be listed once")
    return connectors


class AppManifest(Contract):
    contract_version: ContractVersion
    name: AppId
    owner: UserId
    domain: DomainId
    project_type: ProjectType
    connectors: Annotated[list[ConnectorUse], AfterValidator(_one_use_per_connector)] = Field(
        default_factory=list[ConnectorUse]
    )
    resources: list[Resource] = Field(default_factory=list[Resource])
    audience: Audience
    risk_tier: Annotated[RiskTier | None, Field(json_schema_extra={"readOnly": True})] = None
    """Set by the policy check, never by hand. The builder can't pick a lower tier."""
    expires_on: date
