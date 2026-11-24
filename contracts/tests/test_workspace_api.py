import json
from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl, SecretStr

from studio.contracts.version import CONTRACT_VERSION
from studio.contracts.workspace_api import (
    AddWorktree,
    Bootstrap,
    CommandEvent,
    CommandExit,
    CommandOutput,
    Commit,
    CommitResult,
    CreateBranch,
    Draft,
    FileContent,
    FileEntry,
    FileList,
    GitStatus,
    GitToken,
    Merge,
    MergeResult,
    PreviewStatus,
    Push,
    PushResult,
    Readiness,
    Restore,
    RunCommand,
    WorkspaceApi,
    Worktree,
    WriteFile,
    openapi,
    router,
)

SHA = "a" * 40
RUNNING = PreviewStatus(state="running", url=AnyHttpUrl("https://preview.example/s-7f3a9c/"))

# The operations listed in step 02, plus the four that steps 13 and 14 need:
# draft, git_set_token, preview_stop and readiness.
EXPECTED_OPERATIONS = {
    "run_command",
    "read_file",
    "write_file",
    "list_files",
    "git_status",
    "git_commit",
    "git_create_branch",
    "git_add_worktree",
    "git_remove_worktree",
    "git_merge",
    "git_push",
    "git_set_token",
    "preview_start",
    "preview_stop",
    "preview_status",
    "draft",
    "bootstrap",
    "restore",
    "health",
    "readiness",
}


class FakeWorkspace:
    """Records what reaches the workspace, and answers with fixed values."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.ready = Readiness(ready=True)

    async def run_command(self, command: RunCommand) -> AsyncIterator[CommandEvent]:
        self.calls.append(("run_command", command))
        yield CommandOutput(type="output", stream="stdout", text="Resolved 42 packages\n")
        yield CommandExit(type="exit", exit_code=0, timed_out=False)

    async def read_file(self, path: str) -> FileContent:
        self.calls.append(("read_file", path))
        return FileContent(path=path, content="hello\n")

    async def write_file(self, file: WriteFile) -> None:
        self.calls.append(("write_file", file))

    async def list_files(self, path: str) -> FileList:
        self.calls.append(("list_files", path))
        return FileList(entries=[FileEntry(path="src", kind="directory")])

    async def git_status(self) -> GitStatus:
        return GitStatus(branch="build/staff-requests", clean=True, changed=[])

    async def git_commit(self, commit: Commit) -> CommitResult:
        self.calls.append(("git_commit", commit))
        return CommitResult(sha=SHA)

    async def git_create_branch(self, branch: CreateBranch) -> None:
        self.calls.append(("git_create_branch", branch))

    async def git_add_worktree(self, worktree: AddWorktree) -> Worktree:
        return Worktree(
            name=worktree.name, path=f".worktrees/{worktree.name}", branch=worktree.branch
        )

    async def git_remove_worktree(self, name: str) -> None:
        self.calls.append(("git_remove_worktree", name))

    async def git_merge(self, merge: Merge) -> MergeResult:
        return MergeResult(merged=True, sha=SHA, conflicts=[])

    async def git_push(self, push: Push) -> PushResult:
        return PushResult(branch=push.branch, sha=SHA)

    async def git_set_token(self, token: GitToken) -> None:
        self.calls.append(("git_set_token", token))

    async def preview_start(self) -> PreviewStatus:
        return RUNNING

    async def preview_stop(self) -> PreviewStatus:
        return PreviewStatus(state="stopped")

    async def preview_status(self) -> PreviewStatus:
        return RUNNING

    async def draft(self, draft: Draft) -> PreviewStatus:
        self.calls.append(("draft", draft))
        return PreviewStatus(state="starting")

    async def bootstrap(self, bootstrap: Bootstrap) -> PreviewStatus:
        self.calls.append(("bootstrap", bootstrap))
        return RUNNING

    async def restore(self, restore: Restore) -> PreviewStatus:
        self.calls.append(("restore", restore))
        return RUNNING

    async def readiness(self) -> Readiness:
        return self.ready


@pytest.fixture
def workspace() -> FakeWorkspace:
    return FakeWorkspace()


@pytest.fixture
def client(workspace: FakeWorkspace) -> TestClient:
    implementation: WorkspaceApi = workspace
    app = FastAPI()
    app.state.workspace = implementation
    app.include_router(router)
    return TestClient(app)


def test_openapi_lists_every_operation_and_the_contracts_version() -> None:
    spec = openapi()
    operations = {op["operationId"] for path in spec["paths"].values() for op in path.values()}

    assert operations == EXPECTED_OPERATIONS
    assert spec["info"]["version"] == CONTRACT_VERSION


def test_openapi_documents_the_command_stream_as_ndjson() -> None:
    run = openapi()["paths"]["/commands"]["post"]

    assert "application/x-ndjson" in run["responses"]["200"]["content"]


def test_run_command_streams_output_then_the_exit(client: TestClient) -> None:
    response = client.post("/commands", json={"argv": ["uv", "sync"], "timeout_seconds": 600})

    lines = [json.loads(line) for line in response.text.splitlines()]
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert lines == [
        {"type": "output", "stream": "stdout", "text": "Resolved 42 packages\n"},
        {"type": "exit", "exit_code": 0, "timed_out": False},
    ]


@pytest.mark.parametrize("path", ["../.git/config", "/etc/passwd", "src/../../secrets"])
def test_paths_outside_the_repo_are_refused(
    client: TestClient, workspace: FakeWorkspace, path: str
) -> None:
    write = client.put("/files/content", json={"path": path, "content": "x"})
    read = client.get("/files/content", params={"path": path})

    assert (write.status_code, read.status_code) == (422, 422)
    assert workspace.calls == []


def test_calls_reach_the_workspace_with_typed_bodies(
    client: TestClient, workspace: FakeWorkspace
) -> None:
    commit = client.post("/git/commits", json={"message": "feat: add the request form"})
    removed = client.delete("/git/worktrees/ticket-3")

    assert commit.json() == {"sha": SHA}
    assert removed.status_code == 204
    assert workspace.calls == [
        ("git_commit", Commit(message="feat: add the request form")),
        ("git_remove_worktree", "ticket-3"),
    ]


def test_the_github_token_reaches_the_workspace_but_is_never_shown(
    client: TestClient, workspace: FakeWorkspace
) -> None:
    token = GitToken(token=SecretStr("not-a-real-token"))

    response = client.put(
        "/git/token",
        content=token.model_dump_json(),
        headers={"content-type": "application/json"},
    )

    (_, received) = workspace.calls[0]
    assert response.status_code == 204
    assert isinstance(received, GitToken)
    assert received.token.get_secret_value() == "not-a-real-token"
    assert "not-a-real-token" not in repr(received)


def test_readiness_answers_503_until_the_workspace_is_ready(
    client: TestClient, workspace: FakeWorkspace
) -> None:
    workspace.ready = Readiness(ready=False, detail="Installing dependencies")
    starting = client.get("/ready")
    workspace.ready = Readiness(ready=True)
    ready = client.get("/ready")

    assert (starting.status_code, starting.json()["detail"]) == (503, "Installing dependencies")
    assert ready.status_code == 200


def test_health_needs_no_workspace_call(client: TestClient, workspace: FakeWorkspace) -> None:
    response = client.get("/health")

    assert response.json() == {"status": "ok", "service": "workspace"}
    assert workspace.calls == []
