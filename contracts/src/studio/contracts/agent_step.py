"""The agent step message: one Cloud Tasks payload per agent step."""

from typing import Annotated, Literal

from pydantic import StringConstraints

from studio.contracts.common import CallContext, Contract
from studio.contracts.version import ContractVersion

type AgentStepKind = Literal["intake", "router", "fast", "lead", "worker"]
type IdempotencyKey = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9._:-]{8,128}$")]
"""Retries of the same step reuse it, so the step runs once."""


class AgentStep(Contract):
    contract_version: ContractVersion
    context: CallContext
    kind: AgentStepKind
    input: Annotated[str, StringConstraints(min_length=1, max_length=20_000)]
    """The builder's message, or the instruction for this step."""
    idempotency_key: IdempotencyKey
