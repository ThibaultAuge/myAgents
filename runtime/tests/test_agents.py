from __future__ import annotations

from pathlib import Path

import pytest

from gatekeeper_runtime.agents import load_agent
from gatekeeper_runtime.config import load_runtime_paths


def _write_agent(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_load_agent_prefers_project_override(tmp_path: Path) -> None:
    """Verifies that project agent files override matching global agent files."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)

    _write_agent(
        global_agents_dir / "primary" / "Dora the Explorer.md",
        "---\nmode: primary\n---\nGlobal prompt",
    )
    _write_agent(
        paths.project_agents_dir / "primary" / "Dora the Explorer.md",
        "---\nmode: primary\n---\nProject prompt",
    )

    agent = load_agent(paths, "primary/Dora the Explorer.md")

    assert agent.prompt == "Project prompt"
    assert agent.frontmatter["mode"] == "primary"


def test_load_agent_falls_back_to_global_file(tmp_path: Path) -> None:
    """Verifies that global agent file is loaded when no project override exists."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)

    _write_agent(
        global_agents_dir / "primary" / "Bob the Builder.md",
        "---\ndescription: Builder\n---\nGlobal builder prompt",
    )

    agent = load_agent(paths, "primary/Bob the Builder.md")

    assert agent.name == "Bob the Builder"
    assert agent.prompt == "Global builder prompt"
    assert agent.frontmatter["description"] == "Builder"


def test_load_agent_raises_for_missing_file(tmp_path: Path) -> None:
    """Verifies that missing agent files raise FileNotFoundError."""
    paths = load_runtime_paths(tmp_path / "project", tmp_path / "global-agents")

    with pytest.raises(FileNotFoundError):
        load_agent(paths, "primary/Missing Agent.md")


def test_load_agent_rejects_missing_frontmatter(tmp_path: Path) -> None:
    """Verifies that agent files without YAML frontmatter raise ValueError."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)

    _write_agent(paths.project_agents_dir / "primary" / "Broken.md", "Prompt only")

    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        load_agent(paths, "primary/Broken.md")


def test_load_agent_accepts_crlf_frontmatter(tmp_path: Path) -> None:
    """Verifies that valid CRLF markdown frontmatter loads on Windows."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)

    _write_agent(
        global_agents_dir / "primary" / "Windows Agent.md",
        "---\r\ndescription: Windows\r\n---\r\nPrompt",
    )

    agent = load_agent(paths, "primary/Windows Agent.md")

    assert agent.frontmatter["description"] == "Windows"
    assert agent.prompt == "Prompt"


def test_load_agent_rejects_path_escape(tmp_path: Path) -> None:
    """Verifies that agent loading cannot escape the configured agent directories."""
    paths = load_runtime_paths(tmp_path / "project", tmp_path / "global-agents")

    with pytest.raises(ValueError, match="escaped base directory"):
        load_agent(paths, "../outside.md")
