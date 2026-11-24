"""Pub/Sub events, as CloudEvents 1.0 in structured JSON mode.

`type` is the event name, such as `session.started`, and `data` is typed per event. The
`contractversion` extension attribute carries the contracts version the event was written with.
"""

from typing import Annotated, Literal, get_args

from pydantic import AwareDatetime, Field, PositiveInt, StringConstraints

from studio.contracts.common import (
    AppId,
    BranchName,
    CallContext,
    CommitSha,
    Contract,
    Environment,
)
from studio.contracts.version import ContractVersion


class CloudEvent(Contract):
    specversion: Literal["1.0"] = "1.0"
    id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    source: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    """The producer, as a URI reference such as `/services/session-manager`."""
    time: AwareDatetime
    datacontenttype: Literal["application/json"] = "application/json"
    contractversion: ContractVersion


# Event data. Session-scoped events carry the three IDs; app-scoped ones carry the app ID.
class SessionData(Contract):
    context: CallContext


class TicketData(Contract):
    context: CallContext
    ticket: PositiveInt
    """The GitHub issue number."""
    state: Literal["open", "in-progress", "done"]


class MergeData(Contract):
    context: CallContext
    branch: BranchName
    """The branch merged into the build branch."""
    sha: CommitSha


class PreviewData(Contract):
    context: CallContext
    sha: CommitSha


class CheckData(Contract):
    app_id: AppId
    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    conclusion: Literal[
        "success", "failure", "neutral", "cancelled", "skipped", "timed_out", "action_required"
    ]


class DeployData(Contract):
    app_id: AppId
    environment: Environment
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    outcome: Literal["success", "failure"]


type ReviewKind = Literal["domain-owner", "engineer", "security", "dpo", "legal"]


class ReviewRequestData(Contract):
    app_id: AppId
    review: ReviewKind


class ReviewResultData(Contract):
    app_id: AppId
    review: ReviewKind
    outcome: Literal["approved", "changes-requested"]


class BudgetData(Contract):
    context: CallContext
    scope: Literal["session", "user-day"]


class SessionStarted(CloudEvent):
    type: Literal["session.started"]
    data: SessionData


class SessionReady(CloudEvent):
    type: Literal["session.ready"]
    data: SessionData


class SessionIdle(CloudEvent):
    type: Literal["session.idle"]
    data: SessionData


class SessionDeleted(CloudEvent):
    type: Literal["session.deleted"]
    data: SessionData


class IntakeConfirmed(CloudEvent):
    type: Literal["intake.confirmed"]
    data: SessionData


class PlanApproved(CloudEvent):
    type: Literal["plan.approved"]
    data: SessionData


class TicketUpdated(CloudEvent):
    type: Literal["ticket.updated"]
    data: TicketData


class MergeDone(CloudEvent):
    type: Literal["merge.done"]
    data: MergeData


class PreviewRefreshed(CloudEvent):
    type: Literal["preview.refreshed"]
    data: PreviewData


class PublishRequested(CloudEvent):
    type: Literal["publish.requested"]
    data: SessionData


class CheckCompleted(CloudEvent):
    type: Literal["check.completed"]
    data: CheckData


class DeployCompleted(CloudEvent):
    type: Literal["deploy.completed"]
    data: DeployData


class ReviewRequested(CloudEvent):
    type: Literal["review.requested"]
    data: ReviewRequestData


class ReviewCompleted(CloudEvent):
    type: Literal["review.completed"]
    data: ReviewResultData


class BudgetExceeded(CloudEvent):
    type: Literal["budget.exceeded"]
    data: BudgetData


type AnyEvent = (
    SessionStarted
    | SessionReady
    | SessionIdle
    | SessionDeleted
    | IntakeConfirmed
    | PlanApproved
    | TicketUpdated
    | MergeDone
    | PreviewRefreshed
    | PublishRequested
    | CheckCompleted
    | DeployCompleted
    | ReviewRequested
    | ReviewCompleted
    | BudgetExceeded
)
type Event = Annotated[AnyEvent, Field(discriminator="type")]

EVENTS: dict[str, type[CloudEvent]] = {
    get_args(model.model_fields["type"].annotation)[0]: model
    for model in get_args(AnyEvent.__value__)
}
"""Every event model, by its CloudEvents `type`."""
