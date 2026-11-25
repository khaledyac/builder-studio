"""The registry record: owner, tier and expiry of every app. No entry, no deploy."""

from datetime import date
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from studio.contracts.common import (
    AppId,
    Contract,
    DomainId,
    Environment,
    Environments,
    RiskTier,
    UserId,
)
from studio.contracts.version import ContractVersion

type RegistryStatus = Literal["draft", "live-lab", "live-prod", "expired", "archived"]
type RepoName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")]
"""A GitHub repository as `owner/name`."""


class RegistryRecord(Contract):
    contract_version: ContractVersion
    app_id: AppId
    owner: UserId
    domain: DomainId
    tier: RiskTier
    expires_on: date
    repo: RepoName
    environments: Environments = Field(default_factory=list[Environment])
    """The environments the app's tier allows it to reach."""
    status: RegistryStatus
