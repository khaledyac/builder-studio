"""Every contract by name. Examples live under `contracts/examples/<name>/`."""

from typing import Any

from pydantic import TypeAdapter

from studio.contracts.agent_step import AgentStep
from studio.contracts.app import AppManifest
from studio.contracts.events import Event
from studio.contracts.need import Need
from studio.contracts.registry import RegistryRecord
from studio.contracts.ui_events import UiEvent
from studio.contracts.workspace_api import RunCommand, WriteFile

SCHEMAS: dict[str, TypeAdapter[Any]] = {
    "need": TypeAdapter(Need),
    "app": TypeAdapter(AppManifest),
    "registry-record": TypeAdapter(RegistryRecord),
    "agent-step": TypeAdapter(AgentStep),
    "event": TypeAdapter(Event),
    "ui-event": TypeAdapter(UiEvent),
}
"""The contracts exported as JSON Schema. The workspace API is exported as OpenAPI instead."""

CONTRACTS: dict[str, TypeAdapter[Any]] = {
    **SCHEMAS,
    "workspace-api/run-command": TypeAdapter(RunCommand),
    "workspace-api/write-file": TypeAdapter(WriteFile),
}
"""Every contract with examples, including the workspace API's main request bodies."""
