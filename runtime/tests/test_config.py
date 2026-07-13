from __future__ import annotations

from pathlib import Path

import pytest

from gatekeeper_runtime.config import load_project_settings, load_runtime_paths


def test_load_runtime_paths_uses_explicit_global_agents_dir(tmp_path: Path) -> None:
    """Verifies that explicit global agents path overrides environment lookup."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    project_root.mkdir()
    global_agents_dir.mkdir()

    paths = load_runtime_paths(project_root, global_agents_dir)

    assert paths.project_root == project_root.resolve()
    assert paths.global_agents_dir == global_agents_dir.resolve()
    assert paths.project_gatekeeper_dir == project_root.resolve() / ".gatekeeper"
    assert paths.project_agents_dir == project_root.resolve() / ".gatekeeper" / "agents"
    assert paths.runs_dir == project_root.resolve() / ".gatekeeper" / "runs"
    assert paths.plans_dir == project_root.resolve() / "plans"


def test_load_runtime_paths_uses_environment_global_agents_dir(tmp_path: Path, monkeypatch) -> None:
    """Verifies that environment global agents path is used when no arg is set."""
    project_root = tmp_path / "project"
    env_agents_dir = tmp_path / "env-agents"
    project_root.mkdir()
    env_agents_dir.mkdir()
    monkeypatch.setenv("GATEKEEPER_GLOBAL_AGENTS_DIR", str(env_agents_dir))

    paths = load_runtime_paths(project_root)

    assert paths.global_agents_dir == env_agents_dir.resolve()


def test_load_runtime_paths_reads_project_yaml_configuration(tmp_path: Path, monkeypatch) -> None:
    """Verifies that project YAML config provides path and model settings."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    config_dir = project_root / ".gatekeeper"
    config_dir.mkdir(parents=True)
    global_agents_dir = tmp_path / "shared-agents"
    global_agents_dir.mkdir()
    (config_dir / "gatekeeper.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                f"  global_agents_dir: {global_agents_dir.as_posix()}",
                "  runs_dir: .gatekeeper/custom-runs",
                "  plans_dir: planning",
                "models:",
                "  provider: openai",
                "  model: gpt-4.1-mini",
                "agents:",
                "  overrides_dir: .gatekeeper/custom-agents",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEKEEPER_GLOBAL_AGENTS_DIR", raising=False)

    settings = load_project_settings(project_root)

    assert settings.paths.global_agents_dir == global_agents_dir.resolve()
    assert settings.paths.project_agents_dir == (project_root / ".gatekeeper" / "custom-agents").resolve()
    assert settings.paths.runs_dir == (project_root / ".gatekeeper" / "custom-runs").resolve()
    assert settings.paths.plans_dir == (project_root / "planning").resolve()
    assert settings.models.model == "gpt-4.1-mini"


def test_load_runtime_paths_requires_global_agents_source(tmp_path: Path, monkeypatch) -> None:
    """Verifies that missing global agent configuration fails clearly."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    monkeypatch.delenv("GATEKEEPER_GLOBAL_AGENTS_DIR", raising=False)

    with pytest.raises(ValueError, match="No global agent library configured"):
        load_runtime_paths(project_root)


def test_project_yaml_rejects_paths_outside_project_root(tmp_path: Path) -> None:
    """Verifies that local project paths cannot escape the project root."""
    project_root = tmp_path / "project"
    config_dir = project_root / ".gatekeeper"
    project_root.mkdir()
    config_dir.mkdir(parents=True)
    global_agents_dir = tmp_path / "shared-agents"
    global_agents_dir.mkdir()
    (config_dir / "gatekeeper.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                f"  global_agents_dir: {global_agents_dir.as_posix()}",
                "  runs_dir: ../outside",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="escapes the project root"):
        load_project_settings(project_root)
