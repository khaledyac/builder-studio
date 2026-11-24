"""The workspace API: what the agent service, session manager and preview proxy call on a session.

The router below is the contract. Step 13 serves it with a real `WorkspaceApi`:

    app.state.workspace = MyWorkspace()
    app.include_router(router)

so the served OpenAPI matches `openapi()` by construction. The router serves `/health` and
`/ready` itself, so don't also mount `studio.common`'s health router. Paths are relative to the
repo root.
"""

from collections.abc import AsyncIterator
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal, Protocol, cast

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import (
    AfterValidator,
    AnyHttpUrl,
    Field,
    SecretStr,
    StringConstraints,
    WithJsonSchema,
    field_serializer,
)

from studio.contracts.app import AppManifest
from studio.contracts.common import BranchName, CommitSha, Contract, DomainId, HealthStatus
from studio.contracts.need import Need
from studio.contracts.registry import RepoName
from studio.contracts.version import CONTRACT_VERSION

NDJSON = "application/x-ndjson"


def _inside_repo(path: str) -> str:
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or "\\" in path or "\0" in path:
        raise ValueError("must be a relative path inside the repository")
    return path


REPO_PATH_PATTERN = r"^(?!/)(?!(?:.*/)?\.\.(?:/|$))[^\\\x00]+$"
"""The same rule as `_inside_repo`, for the generated schema: relative, no `..`, no backslash."""

RepoPath = Annotated[
    str,
    StringConstraints(min_length=1, max_length=500),
    AfterValidator(_inside_repo),
    WithJsonSchema(
        {
            "type": "string",
            "minLength": 1,
            "maxLength": 500,
            "pattern": REPO_PATH_PATTERN,
            "description": "A path relative to the repository root, without `..`.",
        }
    ),
]
WorktreeName = Annotated[str, StringConstraints(pattern=r"^[a-z]([a-z0-9-]*[a-z0-9])?$")]


class RunCommand(Contract):
    argv: Annotated[list[Annotated[str, StringConstraints(min_length=1)]], Field(min_length=1)]
    """The program and its arguments. There is no shell."""
    cwd: RepoPath = "."
    timeout_seconds: Annotated[int, Field(ge=1, le=1800)] = 300


class CommandOutput(Contract):
    type: Literal["output"]
    stream: Literal["stdout", "stderr"]
    text: str


class CommandExit(Contract):
    type: Literal["exit"]
    exit_code: int
    timed_out: bool


CommandEvent = Annotated[CommandOutput | CommandExit, Field(discriminator="type")]
"""One line of a command's NDJSON stream: output lines, then one exit line."""


class FileContent(Contract):
    path: RepoPath
    content: str


class WriteFile(Contract):
    path: RepoPath
    content: Annotated[str, StringConstraints(max_length=1_000_000)]


class FileEntry(Contract):
    path: RepoPath
    kind: Literal["file", "directory"]


class FileList(Contract):
    entries: list[FileEntry]


class GitStatus(Contract):
    branch: BranchName
    clean: bool
    changed: list[RepoPath]


class Commit(Contract):
    message: Annotated[str, StringConstraints(min_length=1, max_length=2000)]
    """Commits every change in the working copy."""


class CommitResult(Contract):
    sha: CommitSha


class CreateBranch(Contract):
    name: BranchName
    """Created from the current branch."""


class AddWorktree(Contract):
    name: WorktreeName
    """One per worker agent, such as `ticket-3`."""
    branch: BranchName


class Worktree(Contract):
    name: WorktreeName
    path: RepoPath
    branch: BranchName


class Merge(Contract):
    branch: BranchName
    into: BranchName


class MergeResult(Contract):
    merged: bool
    sha: CommitSha | None
    conflicts: list[RepoPath]


class Push(Contract):
    branch: BranchName


class PushResult(Contract):
    branch: BranchName
    sha: CommitSha


class GitToken(Contract):
    """A short-lived GitHub token. The workspace keeps it in memory only.

    Its repr stays masked, but its JSON carries the real value: sending it is the point.
    """

    token: SecretStr

    @field_serializer("token", when_used="json")
    def reveal_token(self, token: SecretStr) -> str:
        return token.get_secret_value()


class PreviewStatus(Contract):
    state: Literal["starting", "running", "stopped", "failed"]
    url: AnyHttpUrl | None = None


class Readiness(Contract):
    ready: bool
    detail: Annotated[str, StringConstraints(max_length=500)] | None = None
    """What it's still doing, such as installing dependencies."""


class Draft(Contract):
    """Render a draft from the base and domain layers while the intake runs."""

    domain: DomainId


class Bootstrap(Contract):
    """Apply the project type layer with the confirmed answers."""

    need: Need
    app: AppManifest


class Restore(Contract):
    """Rebuild the working copy from the app's build branch."""

    repo: RepoName
    branch: BranchName


class WorkspaceApi(Protocol):
    """What a workspace implements. Step 13 provides the real one."""

    def run_command(self, command: RunCommand) -> AsyncIterator[CommandEvent]: ...
    async def read_file(self, path: RepoPath) -> FileContent: ...
    async def write_file(self, file: WriteFile) -> None: ...
    async def list_files(self, path: RepoPath) -> FileList: ...
    async def git_status(self) -> GitStatus: ...
    async def git_commit(self, commit: Commit) -> CommitResult: ...
    async def git_create_branch(self, branch: CreateBranch) -> None: ...
    async def git_add_worktree(self, worktree: AddWorktree) -> Worktree: ...
    async def git_remove_worktree(self, name: WorktreeName) -> None: ...
    async def git_merge(self, merge: Merge) -> MergeResult: ...
    async def git_push(self, push: Push) -> PushResult: ...
    async def git_set_token(self, token: GitToken) -> None: ...
    async def preview_start(self) -> PreviewStatus: ...
    async def preview_stop(self) -> PreviewStatus: ...
    async def preview_status(self) -> PreviewStatus: ...
    async def draft(self, draft: Draft) -> PreviewStatus: ...
    async def bootstrap(self, bootstrap: Bootstrap) -> PreviewStatus: ...
    async def restore(self, restore: Restore) -> PreviewStatus: ...
    async def readiness(self) -> Readiness: ...


def _workspace(request: Request) -> WorkspaceApi:
    workspace = getattr(request.app.state, "workspace", None)
    if workspace is None:
        raise RuntimeError("set app.state.workspace to a WorkspaceApi before serving the router")
    return cast(WorkspaceApi, workspace)


Workspace = Annotated[WorkspaceApi, Depends(_workspace)]


class _NdjsonDoc(JSONResponse):
    """Documents a typed NDJSON stream. FastAPI only documents a response model for JSON
    responses, so the route declares this class while the endpoint returns a StreamingResponse."""

    media_type = NDJSON


async def _ndjson(events: AsyncIterator[CommandEvent]) -> AsyncIterator[str]:
    async for event in events:
        yield event.model_dump_json() + "\n"


router = APIRouter()


@router.post(
    "/commands",
    operation_id="run_command",
    response_class=_NdjsonDoc,
    response_model=CommandEvent,
    response_description="One JSON object per line: output lines, then one exit line.",
)
async def run_command(command: RunCommand, workspace: Workspace) -> StreamingResponse:
    return StreamingResponse(_ndjson(workspace.run_command(command)), media_type=NDJSON)


@router.get("/files/content", operation_id="read_file")
async def read_file(path: RepoPath, workspace: Workspace) -> FileContent:
    return await workspace.read_file(path)


@router.put("/files/content", operation_id="write_file", status_code=204)
async def write_file(file: WriteFile, workspace: Workspace) -> None:
    await workspace.write_file(file)


@router.get("/files", operation_id="list_files")
async def list_files(workspace: Workspace, path: RepoPath = ".") -> FileList:
    return await workspace.list_files(path)


@router.get("/git/status", operation_id="git_status")
async def git_status(workspace: Workspace) -> GitStatus:
    return await workspace.git_status()


@router.post("/git/commits", operation_id="git_commit")
async def git_commit(commit: Commit, workspace: Workspace) -> CommitResult:
    return await workspace.git_commit(commit)


@router.post("/git/branches", operation_id="git_create_branch", status_code=204)
async def git_create_branch(branch: CreateBranch, workspace: Workspace) -> None:
    await workspace.git_create_branch(branch)


@router.post("/git/worktrees", operation_id="git_add_worktree")
async def git_add_worktree(worktree: AddWorktree, workspace: Workspace) -> Worktree:
    return await workspace.git_add_worktree(worktree)


@router.delete("/git/worktrees/{name}", operation_id="git_remove_worktree", status_code=204)
async def git_remove_worktree(name: WorktreeName, workspace: Workspace) -> None:
    await workspace.git_remove_worktree(name)


@router.post("/git/merges", operation_id="git_merge")
async def git_merge(merge: Merge, workspace: Workspace) -> MergeResult:
    return await workspace.git_merge(merge)


@router.post("/git/pushes", operation_id="git_push")
async def git_push(push: Push, workspace: Workspace) -> PushResult:
    return await workspace.git_push(push)


@router.put("/git/token", operation_id="git_set_token", status_code=204)
async def git_set_token(token: GitToken, workspace: Workspace) -> None:
    await workspace.git_set_token(token)


@router.post("/preview/start", operation_id="preview_start")
async def preview_start(workspace: Workspace) -> PreviewStatus:
    return await workspace.preview_start()


@router.post("/preview/stop", operation_id="preview_stop")
async def preview_stop(workspace: Workspace) -> PreviewStatus:
    return await workspace.preview_stop()


@router.get("/preview", operation_id="preview_status")
async def preview_status(workspace: Workspace) -> PreviewStatus:
    return await workspace.preview_status()


@router.post("/draft", operation_id="draft")
async def draft(draft: Draft, workspace: Workspace) -> PreviewStatus:
    return await workspace.draft(draft)


@router.post("/bootstrap", operation_id="bootstrap")
async def bootstrap(bootstrap: Bootstrap, workspace: Workspace) -> PreviewStatus:
    return await workspace.bootstrap(bootstrap)


@router.post("/restore", operation_id="restore")
async def restore(restore: Restore, workspace: Workspace) -> PreviewStatus:
    return await workspace.restore(restore)


@router.get("/health", operation_id="health")
async def health() -> HealthStatus:
    return HealthStatus(service="workspace")


@router.get(
    "/ready",
    operation_id="readiness",
    responses={503: {"model": Readiness, "description": "Not ready yet."}},
)
async def readiness(workspace: Workspace, response: Response) -> Readiness:
    status = await workspace.readiness()
    if not status.ready:
        response.status_code = 503
    return status


def openapi() -> dict[str, Any]:
    """The workspace API's OpenAPI document, versioned with the contracts."""
    app = FastAPI(
        title="Workspace API",
        version=CONTRACT_VERSION,
        description="Called on a session's workspace by the agent service, the session "
        "manager and the preview proxy. Builder Studio contracts.",
    )
    app.include_router(router)
    return app.openapi()
