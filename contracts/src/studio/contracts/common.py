"""Types shared by the contracts."""

from typing import Annotated, Literal, TypeAliasType, get_args

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

SLUG = r"^[a-z]([a-z0-9-]*[a-z0-9])?$"
"""Lowercase letters, digits and inner hyphens: fits DNS labels and Cloud Run names."""


class Contract(BaseModel):
    """Base for every contract: immutable, and tolerant of fields added by a newer minor version."""

    model_config = ConfigDict(frozen=True, extra="ignore")


class StrictContract(Contract):
    """For documents people and agents edit by hand (`need.yml`, `app.yaml`): an unknown key is
    an error, because ignoring a misspelled one could hide data access and lower the tier."""

    model_config = ConfigDict(extra="forbid")


# IDs. Slugs fit in DNS labels and Cloud Run names: app names end up in `<app>.lab.<domain>`.
type UserId = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9]{1,64}$")]
"""An Okta user ID."""
type AppId = Annotated[str, StringConstraints(pattern=SLUG, max_length=40)]
type DomainId = Annotated[str, StringConstraints(pattern=SLUG, max_length=20)]
type ConnectorId = Annotated[str, StringConstraints(pattern=SLUG, max_length=63)]
type SessionId = Annotated[str, StringConstraints(pattern=SLUG, max_length=32)]

type Line = Annotated[str, StringConstraints(min_length=1, max_length=500)]
"""One line of plain text, such as an example, a question or a reason."""

type ProjectType = Literal["form-workflow", "dashboard", "chat-assistant", "records", "adk-agent"]
type Audience = Literal["personal", "team", "domain"]
"""Who can use the app: its author only, a team, or everyone in the domain."""
type AccessMode = Literal["read", "write"]
type DataClassification = Literal["internal", "client", "unknown"]
"""`internal` is internal, non-sensitive data. `client` is client data. `unknown` is treated as
the most sensitive."""
type RiskTier = Literal[1, 2, 3]
type Environment = Literal["lab", "staging", "production"]
type SessionState = Literal["starting", "ready", "building", "idle", "rebuilding", "deleted"]
"""The workspace lifecycle in architecture §5."""
type CommitSha = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
type BranchName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9._/-]{1,200}$")]


def _unique[T](items: list[T]) -> list[T]:
    if len(set(items)) != len(items):
        raise ValueError("items must be unique")
    return items


type ConnectorIds = Annotated[
    list[ConnectorId], AfterValidator(_unique), Field(json_schema_extra={"uniqueItems": True})
]
type Environments = Annotated[
    list[Environment], AfterValidator(_unique), Field(json_schema_extra={"uniqueItems": True})
]


class CallContext(Contract):
    """The IDs that travel together: every model call, log line and agent step carries them."""

    user_id: UserId
    app_id: AppId
    session_id: SessionId


class HealthStatus(Contract):
    status: Literal["ok"] = "ok"
    service: str


def by_type(union: TypeAliasType) -> dict[str, type[Contract]]:
    """Each model in a union alias, by the value of its `type` field."""
    return {
        get_args(model.model_fields["type"].annotation)[0]: model
        for model in get_args(union.__value__)
    }
