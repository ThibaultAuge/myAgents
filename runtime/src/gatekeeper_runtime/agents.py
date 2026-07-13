from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import RuntimePaths


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    path: Path
    frontmatter: dict
    prompt: str


def _resolve_within(base_dir: Path, relative_path: str) -> Path:
    candidate = (base_dir / relative_path).resolve()
    base_resolved = base_dir.resolve()
    try:
        candidate.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError(f"Agent path escaped base directory: {relative_path}") from exc
    return candidate


def _read_agent_file(path: Path) -> AgentDefinition:
    raw = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not raw.startswith("---\n"):
        raise ValueError(f"Agent file missing YAML frontmatter: {path}")

    try:
        _, frontmatter_raw, prompt = raw.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"Invalid frontmatter delimiters in {path}") from exc

    frontmatter = yaml.safe_load(frontmatter_raw) or {}
    return AgentDefinition(
        name=path.stem,
        path=path,
        frontmatter=frontmatter,
        prompt=prompt.strip(),
    )


def load_agent(paths: RuntimePaths, relative_path: str) -> AgentDefinition:
    project_override = _resolve_within(paths.project_agents_dir, relative_path)
    if project_override.exists():
        return _read_agent_file(project_override)

    global_path = _resolve_within(paths.global_agents_dir, relative_path)
    if global_path.exists():
        return _read_agent_file(global_path)

    raise FileNotFoundError(f"Agent not found in project override or global library: {relative_path}")
