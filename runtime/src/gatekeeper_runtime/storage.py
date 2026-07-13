from __future__ import annotations

import json
from pathlib import Path
import re

from .state import RunState


SAFE_RUN_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def run_state_path(runs_dir: Path, run_id: str) -> Path:
    if not SAFE_RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"Unsafe run_id: {run_id!r}")

    path = (runs_dir / f"{run_id}.json").resolve()
    runs_dir_resolved = runs_dir.resolve()
    try:
        path.relative_to(runs_dir_resolved)
    except ValueError as exc:
        raise ValueError(f"Run state path escaped runs directory for run_id: {run_id!r}") from exc

    return path


def save_run_state(runs_dir: Path, state: RunState) -> Path:
    path = run_state_path(runs_dir, state.run_id)
    ensure_parent(path)
    state.touch()
    path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_run_state(runs_dir: Path, run_id: str) -> RunState:
    path = run_state_path(runs_dir, run_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    return RunState.model_validate(data)
