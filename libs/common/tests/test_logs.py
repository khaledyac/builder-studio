import io
import json
import logging
from collections.abc import Iterator
from datetime import datetime

import pytest

from studio.common.logs import configure_logging, log_context

ID_FIELDS = {"user_id", "app_id", "session_id"}


@pytest.fixture
def stream() -> Iterator[io.StringIO]:
    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level
    buffer = io.StringIO()
    configure_logging(level="DEBUG", stream=buffer)
    yield buffer
    root.handlers[:] = saved_handlers
    root.setLevel(saved_level)


def events(stream: io.StringIO) -> list[dict[str, object]]:
    return [json.loads(line) for line in stream.getvalue().splitlines()]


def test_each_event_is_one_json_line(stream: io.StringIO) -> None:
    log = logging.getLogger("svc")
    log.info("first")
    log.warning("second\nspans two lines")

    assert len(stream.getvalue().splitlines()) == 2
    assert [event["message"] for event in events(stream)] == ["first", "second\nspans two lines"]


def test_event_has_time_severity_and_logger(stream: io.StringIO) -> None:
    logging.getLogger("svc").error("boom")

    (event,) = events(stream)
    assert event["severity"] == "ERROR"
    assert event["logger"] == "svc"
    assert isinstance(event["time"], str)
    assert datetime.fromisoformat(event["time"]).tzinfo is not None


def test_ids_are_included_when_set(stream: io.StringIO) -> None:
    with log_context(user_id="u-1", app_id="a-1", session_id="s-1"):
        logging.getLogger("svc").info("inside")

    (event,) = events(stream)
    assert event["user_id"] == "u-1"
    assert event["app_id"] == "a-1"
    assert event["session_id"] == "s-1"


def test_ids_are_omitted_when_not_set(stream: io.StringIO) -> None:
    logging.getLogger("svc").info("outside")

    (event,) = events(stream)
    assert not ID_FIELDS & event.keys()


def test_only_the_ids_that_are_set_appear(stream: io.StringIO) -> None:
    with log_context(user_id="u-1"):
        logging.getLogger("svc").info("partial")

    (event,) = events(stream)
    assert event["user_id"] == "u-1"
    assert not {"app_id", "session_id"} & event.keys()


def test_nested_contexts_merge_and_restore(stream: io.StringIO) -> None:
    log = logging.getLogger("svc")
    with log_context(user_id="u-1"):
        with log_context(session_id="s-1"):
            log.info("nested")
        log.info("after inner")
    log.info("after outer")

    nested, after_inner, after_outer = events(stream)
    assert (nested["user_id"], nested["session_id"]) == ("u-1", "s-1")
    assert after_inner["user_id"] == "u-1"
    assert "session_id" not in after_inner
    assert not ID_FIELDS & after_outer.keys()


def test_exception_stays_on_the_same_line(stream: io.StringIO) -> None:
    def fail() -> None:
        raise ValueError("bad input")

    try:
        fail()
    except ValueError:
        logging.getLogger("svc").exception("failed")

    (event,) = events(stream)
    assert event["message"] == "failed"
    assert isinstance(event["exception"], str)
    assert "ValueError: bad input" in event["exception"]


def test_configuring_twice_does_not_duplicate_events(stream: io.StringIO) -> None:
    configure_logging(level="INFO", stream=stream)
    logging.getLogger("svc").info("once")

    assert len(events(stream)) == 1


def test_level_filters_lower_events(stream: io.StringIO) -> None:
    configure_logging(level="WARNING", stream=stream)
    log = logging.getLogger("svc")
    log.info("dropped")
    log.warning("kept")

    assert [event["message"] for event in events(stream)] == ["kept"]
