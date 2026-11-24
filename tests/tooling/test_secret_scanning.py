"""The secret scanners reject a fake secret.

Covers both scanners with the hook definitions in `.pre-commit-config.yaml`: the `gitleaks` hook
on staged changes (every commit), and the `gitleaks-history` scan that `task secrets` runs in CI.
The fake token is generated at runtime, so no secret-shaped string is ever committed.
"""

import secrets
import string
import subprocess
import sys
from pathlib import Path

import pytest

CONFIG = Path(__file__).resolve().parents[2] / ".pre-commit-config.yaml"


def fake_github_token() -> str:
    alphabet = string.ascii_letters + string.digits
    return "ghp_" + "".join(secrets.choice(alphabet) for _ in range(36))


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args], cwd=repo, check=True, capture_output=True
    )


def run_hook(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "--config", str(CONFIG), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "--quiet")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "README.md").write_text("A clean repository.\n")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "--quiet", "--no-verify", "--message", "chore: start")
    return tmp_path


def add_secret(repo: Path) -> None:
    (repo / "settings.py").write_text(f'GITHUB_TOKEN = "{fake_github_token()}"\n')
    git(repo, "add", "settings.py")


def test_commit_hook_rejects_a_staged_secret(repo: Path) -> None:
    add_secret(repo)

    result = run_hook(repo, "gitleaks")

    assert result.returncode != 0, result.stdout
    assert "leaks found" in result.stdout


def test_history_scan_rejects_a_committed_secret(repo: Path) -> None:
    add_secret(repo)
    git(repo, "commit", "--quiet", "--no-verify", "--message", "feat: add settings")

    result = run_hook(repo, "gitleaks-history", "--hook-stage", "manual")

    assert result.returncode != 0, result.stdout
    assert "leaks found" in result.stdout


def test_history_scan_passes_a_clean_repository(repo: Path) -> None:
    result = run_hook(repo, "gitleaks-history", "--hook-stage", "manual")

    assert result.returncode == 0, result.stdout
