import json
from pathlib import Path

from pydantic import TypeAdapter

from studio.contracts.ui_events import UI_EVENTS, QuestionCard, UiEvent

# The list in docs/plan/steps/02-contracts-and-schemas.md: message, question card, summary card,
# plan card, status, preview refresh, cost.
STEP_02_UI_EVENT_TYPES = {
    "message",
    "question-card",
    "summary-card",
    "plan-card",
    "status",
    "preview-refresh",
    "cost",
}


def test_every_ui_event_in_the_step_has_a_model() -> None:
    assert set(UI_EVENTS) == STEP_02_UI_EVENT_TYPES


def test_a_ui_event_is_parsed_into_the_model_for_its_type() -> None:
    payload = {
        "id": "42",
        "type": "question-card",
        "question": "Who will use the app?",
        "suggested_answers": ["Just me", "My team", "Everyone in Retail"],
    }

    event = TypeAdapter(UiEvent).validate_python(payload)

    assert isinstance(event, QuestionCard)
    assert event.suggested_answers[0] == "Just me"


def test_every_ui_event_type_has_a_valid_example() -> None:
    examples = Path(__file__).resolve().parents[1] / "examples" / "ui-event" / "valid"
    covered = {json.loads(path.read_text())["type"] for path in examples.glob("*.json")}

    assert covered == set(UI_EVENTS)
