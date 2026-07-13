from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import yaml


@dataclass(frozen=True)
class RuntimePaths:
    project_root: Path
    global_agents_dir: Path
    project_gatekeeper_dir: Path
    project_agents_dir: Path
    runs_dir: Path
    plans_dir: Path


@dataclass(frozen=True)
class ModelSettings:
    provider: str = "openai"
    model: str = "gpt-4.1"


@dataclass(frozen=True)
class ProjectSettings:
    paths: RuntimePaths
    models: ModelSettings


def _load_project_config(project_root: Path) -> dict:
    config_path = project_root / ".gatekeeper" / "gatekeeper.yaml"
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _resolve_project_local(project_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        raise ValueError(f"Project-local path must stay under the project root, got absolute path: {raw_path}")

    resolved = (project_root / candidate).resolve()
    project_root_resolved = project_root.resolve()
    try:
        resolved.relative_to(project_root_resolved)
    except ValueError as exc:
        raise ValueError(f"Project-local path escapes the project root: {raw_path}") from exc

    return resolved


def load_runtime_paths(project_root: str | Path, global_agents_dir: str | Path | None = None) -> RuntimePaths:
    return load_project_settings(project_root, global_agents_dir).paths


def load_project_settings(project_root: str | Path, global_agents_dir: str | Path | None = None) -> ProjectSettings:
    project_root = Path(project_root).resolve()
    gatekeeper_dir = project_root / ".gatekeeper"
    config = _load_project_config(project_root)
    runtime_cfg = config.get("runtime", {})
    models_cfg = config.get("models", {})
    agents_cfg = config.get("agents", {})

    inferred_global = (
        global_agents_dir
        or os.getenv("GATEKEEPER_GLOBAL_AGENTS_DIR")
        or runtime_cfg.get("global_agents_dir")
    )
    if inferred_global is None:
        raise ValueError(
            "No global agent library configured. Set --global-agents-dir, "
            "GATEKEEPER_GLOBAL_AGENTS_DIR, or .gatekeeper/gatekeeper.yaml runtime.global_agents_dir."
        )

    runs_dir = runtime_cfg.get("runs_dir", ".gatekeeper/runs")
    plans_dir = runtime_cfg.get("plans_dir", "plans")
    overrides_dir = agents_cfg.get("overrides_dir", ".gatekeeper/agents")

    paths = RuntimePaths(
        project_root=project_root,
        global_agents_dir=Path(inferred_global).resolve(),
        project_gatekeeper_dir=gatekeeper_dir,
        project_agents_dir=_resolve_project_local(project_root, overrides_dir),
        runs_dir=_resolve_project_local(project_root, runs_dir),
        plans_dir=_resolve_project_local(project_root, plans_dir),
    )

    return ProjectSettings(
        paths=paths,
        models=ModelSettings(
            provider=models_cfg.get("provider", os.getenv("GATEKEEPER_MODEL_PROVIDER", "openai")),
            model=models_cfg.get("model", os.getenv("GATEKEEPER_MODEL", "gpt-4.1")),
        ),
    )
