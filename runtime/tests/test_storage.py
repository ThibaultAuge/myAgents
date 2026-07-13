from __future__ import annotations

from pathlib import Path

import pytest

from gatekeeper_runtime.state import RunState
from gatekeeper_runtime.storage import load_run_state, run_state_path, save_run_state


def test_run_state_path_uses_json_extension(tmp_path: Path) -> None:
    """Verifies that run state paths are stored under the run ID JSON filename."""
    path = run_state_path(tmp_path, "run-123")

    assert path == tmp_path / "run-123.json"


def test_save_and_load_run_state_round_trip(tmp_path: Path, monkeypatch) -> None:
    """Verifies that saved run state can be loaded back with persisted fields."""
    monkeypatch.setattr("gatekeeper_runtime.state.now_iso", lambda: "2026-07-09T00:00:00+00:00")
    state = RunState(user_request="Ship the feature")
    state.plan_file = "plans/runs/run-123-plan.md"
    state.approved = True

    path = save_run_state(tmp_path / "runs", state)
    loaded = load_run_state(tmp_path / "runs", state.run_id)

    assert path.exists()
    assert loaded.run_id == state.run_id
    assert loaded.user_request == "Ship the feature"
    assert loaded.plan_file == "plans/runs/run-123-plan.md"
    assert loaded.approved is True
    assert loaded.updated_at == "2026-07-09T00:00:00+00:00"


def test_run_state_path_rejects_unsafe_run_ids(tmp_path: Path) -> None:
    """Verifies that traversal-like run IDs are rejected before path resolution."""
    with pytest.raises(ValueError, match="Unsafe run_id"):
        run_state_path(tmp_path / "runs", "../escape")
