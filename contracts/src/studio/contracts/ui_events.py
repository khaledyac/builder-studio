"""The events the platform API streams to the web UI, as server-sent events.

Each one is sent with its `type` as the SSE event name and its `id` as the SSE id, so a client
can resume with `Last-Event-ID`.
"""

from typing import Annotated, Literal

from pydantic import AnyHttpUrl, Field, NonNegativeFloat, NonNegativeInt, StringConstraints

from studio.contracts.common import Contract, Line, RiskTier, SessionState, by_type


class UiEventBase(Contract):
    id: Annotated[str, StringConstraints(min_length=1, max_length=64)]


class Message(UiEventBase):
    type: Literal["message"]
    role: Literal["builder", "agent"]
    text: Annotated[str, StringConstraints(min_length=1, max_length=20_000)]


class QuestionCard(UiEventBase):
    type: Literal["question-card"]
    question: Line
    suggested_answers: Annotated[list[Line], Field(min_length=1, max_length=5)]


class SummaryCard(UiEventBase):
    type: Literal["summary-card"]
    summary: Annotated[list[Line], Field(min_length=1, max_length=12)]
    tier: RiskTier
    tier_reasons: list[Line]


class PlanCard(UiEventBase):
    type: Literal["plan-card"]
    summary: Line
    steps: Annotated[list[Line], Field(min_length=1, max_length=20)]


class Status(UiEventBase):
    type: Literal["status"]
    state: SessionState
    detail: Line | None = None


class PreviewRefresh(UiEventBase):
    type: Literal["preview-refresh"]
    url: AnyHttpUrl


class Cost(UiEventBase):
    type: Literal["cost"]
    tokens: NonNegativeInt
    cost_usd: NonNegativeFloat


type AnyUiEvent = Message | QuestionCard | SummaryCard | PlanCard | Status | PreviewRefresh | Cost
type UiEvent = Annotated[AnyUiEvent, Field(discriminator="type")]

UI_EVENTS: dict[str, type[Contract]] = by_type(AnyUiEvent)
"""Every UI event model, by its `type`."""
