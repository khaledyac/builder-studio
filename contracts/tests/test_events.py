import json
from pathlib import Path

from pydantic import TypeAdapter

from studio.contracts.events import EVENTS, DeployCompleted, Event
from studio.contracts.version import CONTRACT_VERSION

# The list in docs/plan/steps/02-contracts-and-schemas.md.
STEP_02_EVENT_TYPES = {
    "session.started",
    "session.ready",
    "session.idle",
    "session.deleted",
    "intake.confirmed",
    "plan.approved",
    "ticket.updated",
    "merge.done",
    "preview.refreshed",
    "publish.requested",
    "check.completed",
    "deploy.completed",
    "review.requested",
    "review.completed",
    "budget.exceeded",
}


def test_every_event_type_in_the_step_has_a_model() -> None:
    assert set(EVENTS) == STEP_02_EVENT_TYPES


def test_an_event_is_parsed_into_the_model_for_its_type() -> None:
    payload = {
        "specversion": "1.0",
        "id": "deploy-123",
        "source": "/services/webhook-receiver",
        "type": "deploy.completed",
        "time": "2026-11-24T10:00:00Z",
        "contractversion": CONTRACT_VERSION,
        "data": {
            "app_id": "staff-requests",
            "environment": "staging",
            "version": "1.4.0",
            "outcome": "success",
        },
    }

    event = TypeAdapter(Event).validate_python(payload)

    assert isinstance(event, DeployCompleted)
    assert (event.data.environment, event.data.version) == ("staging", "1.4.0")


def test_every_event_type_has_a_valid_example() -> None:
    examples = Path(__file__).resolve().parents[1] / "examples" / "event" / "valid"
    covered = {json.loads(path.read_text())["type"] for path in examples.glob("*.json")}

    assert covered == set(EVENTS)
