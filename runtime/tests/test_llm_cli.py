from __future__ import annotations

from pathlib import Path

import pytest

from gatekeeper_runtime.cli import build_parser
from gatekeeper_runtime.contracts import RunStep
from gatekeeper_runtime.llm import build_default_llm
from gatekeeper_runtime.state import RunState
from gatekeeper_runtime.storage import save_run_state


def test_build_default_llm_rejects_unsupported_provider(monkeypatch) -> None:
    """Verifies that unsupported model providers raise a clear ValueError."""
    monkeypatch.setenv("GATEKEEPER_MODEL_PROVIDER", "invalid-provider")

    with pytest.raises(ValueError, match="Unsupported GATEKEEPER_MODEL_PROVIDER"):
        build_default_llm()


def test_build_parser_parses_start_command_arguments(tmp_path: Path) -> None:
    """Verifies that CLI start command requires project path and request text."""
    parser = build_parser()

    args = parser.parse_args(["start", "--project", str(tmp_path), "--request", "Ship it"])

    assert args.command == "start"
    assert args.project == tmp_path
    assert args.request == "Ship it"
    assert args.func.__name__ == "start_run"


def test_build_parser_parses_approve_command_arguments(tmp_path: Path) -> None:
    """Verifies that CLI approve command requires project path and run ID."""
    parser = build_parser()

    args = parser.parse_args(["approve", "--project", str(tmp_path), "--run-id", "run-123"])

    assert args.command == "approve"
    assert args.project == tmp_path
    assert args.run_id == "run-123"
    assert args.func.__name__ == "approve_run"


def test_approve_run_requires_waiting_approval(tmp_path: Path) -> None:
    """Verifies that approval is rejected unless the run is currently waiting."""
    from gatekeeper_runtime.cli import approve_run

    (tmp_path / ".gatekeeper").mkdir(parents=True)
    (tmp_path / ".gatekeeper" / "gatekeeper.yaml").write_text(
        "runtime:\n  global_agents_dir: C:/agents\n",
        encoding="utf-8",
    )
    state = RunState(user_request="Request", current_step=RunStep.DONE)
    save_run_state((tmp_path / ".gatekeeper" / "runs"), state)
    parser = build_parser()
    args = parser.parse_args(["approve", "--project", str(tmp_path), "--run-id", state.run_id])

    with pytest.raises(ValueError, match="is not waiting for approval"):
        approve_run(args)
