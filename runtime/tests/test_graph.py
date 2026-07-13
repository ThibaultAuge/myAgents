from __future__ import annotations

from pathlib import Path

import pytest

from gatekeeper_runtime.agents import load_agent
from gatekeeper_runtime.config import load_runtime_paths
from gatekeeper_runtime.contracts import RunStep
from gatekeeper_runtime.graph import (
    build_node,
    extract_json_block,
    intake_node,
    normalize_plan_file,
    plan_node,
    review_result_node,
    sanitize_token,
)
from gatekeeper_runtime.state import RunState


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeLlm:
    def __init__(self, content: str) -> None:
        self.content = content

    def invoke(self, _: str) -> FakeResponse:
        return FakeResponse(self.content)


def _write_agent(path: Path, prompt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nmode: primary\n---\n{prompt}", encoding="utf-8")


def test_extract_json_block_parses_fenced_json() -> None:
    """Verifies that fenced JSON blocks are parsed into dictionaries."""
    parsed = extract_json_block("before\n```json\n{\"status\": \"ok\"}\n```\nafter")

    assert parsed == {"status": "ok"}


def test_extract_json_block_rejects_missing_fence() -> None:
    """Verifies that agent output without fenced JSON raises ValueError."""
    with pytest.raises(ValueError, match="fenced ```json block"):
        extract_json_block('{"status": "ok"}')


def test_direct_llm_mode_rejects_tool_enabled_agents(tmp_path: Path) -> None:
    """Verifies that tool-enabled shared agents cannot run in direct-LLM mode."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)
    agent_path = global_agents_dir / "primary" / "Dora the Explorer.md"
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.write_text("---\ntools:\n  write: true\n---\nPrompt", encoding="utf-8")

    agent = load_agent(paths, "primary/Dora the Explorer.md")
    assert agent.frontmatter["tools"]["write"] is True

    with pytest.raises(RuntimeError, match="Direct LLM mode cannot execute tool-enabled agent"):
        plan_node(RunState(user_request="Request"), llm=FakeLlm("{}"), paths=paths)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Feature Plan 001", "feature-plan-001"),
        ("***", "run"),
    ],
)
def test_sanitize_token_normalizes_user_visible_tokens(value: str, expected: str) -> None:
    """Verifies that run tokens are slugified and blank results fall back to run."""
    assert sanitize_token(value) == expected


@pytest.mark.parametrize(
    ("plan_file", "approved", "expected_step"),
    [
        ("", False, RunStep.PLAN),
        ("plans/run.md", False, RunStep.WAITING_APPROVAL),
        ("plans/run.md", True, RunStep.BUILD),
    ],
)
def test_intake_node_routes_by_plan_and_approval_state(
    plan_file: str,
    approved: bool,
    expected_step: RunStep,
) -> None:
    """Verifies that intake routing matches plan presence and approval state."""
    state = RunState(user_request="Request", plan_file=plan_file, approved=approved)

    result = intake_node(state)

    assert result == {"current_step": expected_step}


def test_plan_node_parses_dora_contract_and_sets_waiting_approval(tmp_path: Path) -> None:
    """Verifies that Dora output updates plan fields and moves run to approval."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)
    _write_agent(global_agents_dir / "primary" / "Dora the Explorer.md", "Plan prompt")
    llm = FakeLlm(
        "```json\n"
        '{"status":"PLAN_READY","plan_file":"plans/runs/run-abc.md","plan_markdown":"# Plan\\n","summary":"Ready","requirements":["A"],"files_to_modify":["README.md"],"complexity":"S","needs_human_approval":true,"questions_remaining":[]}\n'
        "```"
    )
    state = RunState(user_request="Add runtime tests", run_id="run-abc")

    result = plan_node(state, llm=llm, paths=paths)

    assert result["current_step"] == RunStep.WAITING_APPROVAL
    assert result["plan_file"] == "plans/runs/run-abc.md"
    assert result["plan_summary"] == "Ready"
    assert result["artifacts"]["dora_output"]["complexity"] == "S"
    assert (project_root / "plans" / "runs" / "run-abc.md").read_text(encoding="utf-8") == "# Plan\n"


def test_normalize_plan_file_rejects_paths_outside_plans_dir(tmp_path: Path) -> None:
    """Verifies that plan_file values cannot escape the configured plans directory."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)

    with pytest.raises(ValueError, match="escaped plans_dir"):
        normalize_plan_file("../outside.md", paths=paths)


def test_plan_node_rejects_remaining_questions(tmp_path: Path) -> None:
    """Verifies that PLAN_READY cannot carry unresolved questions."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)
    _write_agent(global_agents_dir / "primary" / "Dora the Explorer.md", "Plan prompt")
    llm = FakeLlm(
        "```json\n"
        '{"status":"PLAN_READY","plan_file":"plans/plan-test-run-123.md","plan_markdown":"# Plan\\n","summary":"Ready","requirements":[],"files_to_modify":[],"complexity":"S","needs_human_approval":true,"questions_remaining":["one"]}\n'
        "```"
    )

    with pytest.raises(ValueError, match="cannot include questions_remaining"):
        plan_node(RunState(user_request="Request", run_id="run-123"), llm=llm, paths=paths)


def test_build_node_rejects_file_writes_for_blocked_build(tmp_path: Path) -> None:
    """Verifies that blocked builds cannot still mutate project files."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)
    _write_agent(global_agents_dir / "primary" / "Bob the Builder.md", "Build prompt")
    llm = FakeLlm(
        "```json\n"
        '{"status":"BUILD_BLOCKED","ready_to_ship":"no","implementation_summary":"Blocked","modified_files":[],"file_writes":[{"path":"README.md","content":"updated"}],"pipeline":{"tests":"blocked","review":"not_run","seo":"not_run","accessibility":"not_run","security":"not_run","cleanup":"not_run","ai_context":"not_run","documentation":"not_run"},"blocking_reason":"Stop","non_blocking_findings":[]}\n'
        "```"
    )
    state = RunState(user_request="Request", run_id="run-123", plan_file="plans/plan-run-123.md", plan_summary="Ready", approved=True)

    with pytest.raises(ValueError, match="BUILD_BLOCKED output cannot include file_writes"):
        build_node(state, llm=llm, paths=paths)


def test_build_node_parses_bob_contract_and_sets_review_step(tmp_path: Path) -> None:
    """Verifies that Bob output updates build summary, files, and review state."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)
    _write_agent(global_agents_dir / "primary" / "Bob the Builder.md", "Build prompt")
    llm = FakeLlm(
        "```json\n"
        '{"status":"BUILD_DONE","ready_to_ship":"no","implementation_summary":"Implemented","modified_files":[],"file_writes":[{"path":"README.md","content":"updated"}],"pipeline":{"tests":"passed","review":"passed","seo":"skipped","accessibility":"skipped","security":"passed","cleanup":"passed","ai_context":"skipped","documentation":"passed"},"blocking_reason":"","non_blocking_findings":["Follow-up"]}\n'
        "```"
    )
    state = RunState(
        user_request="Add runtime tests",
        plan_file="plans/runs/run-abc.md",
        plan_summary="Ready",
        approved=True,
        artifacts={
            "dora_output": {
                "status": "PLAN_READY",
                "plan_file": "plans/runs/run-abc.md",
                "plan_markdown": "# Plan\n",
                "summary": "Ready",
                "requirements": ["A"],
                "files_to_modify": ["README.md"],
                "complexity": "S",
                "needs_human_approval": True,
                "questions_remaining": [],
            }
        },
    )

    result = build_node(state, llm=llm, paths=paths)

    assert result["current_step"] == RunStep.REVIEW_RESULT
    assert result["build_summary"] == "Implemented"
    assert result["modified_files"] == ["README.md"]
    assert result["artifacts"]["bob_output"]["ready_to_ship"] == "no"
    assert (project_root / "README.md").read_text(encoding="utf-8") == "updated"


def test_build_node_rejects_writes_outside_approved_plan_scope(tmp_path: Path) -> None:
    """Verifies that direct-LLM file writes must stay within Dora-approved file targets."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)
    _write_agent(global_agents_dir / "primary" / "Bob the Builder.md", "Build prompt")
    llm = FakeLlm(
        "```json\n"
        '{"status":"BUILD_DONE","ready_to_ship":"no","implementation_summary":"Implemented","modified_files":[],"file_writes":[{"path":"package.json","content":"{}"}],"pipeline":{"tests":"passed","review":"passed","seo":"skipped","accessibility":"skipped","security":"passed","cleanup":"passed","ai_context":"skipped","documentation":"passed"},"blocking_reason":"","non_blocking_findings":[]}\n'
        "```"
    )
    state = RunState(
        user_request="Add runtime tests",
        plan_file="plans/runs/run-abc.md",
        plan_summary="Ready",
        approved=True,
        artifacts={
            "dora_output": {
                "status": "PLAN_READY",
                "plan_file": "plans/runs/run-abc.md",
                "plan_markdown": "# Plan\n",
                "summary": "Ready",
                "requirements": ["A"],
                "files_to_modify": ["README.md"],
                "complexity": "S",
                "needs_human_approval": True,
                "questions_remaining": [],
            }
        },
    )

    with pytest.raises(ValueError, match="outside the approved plan scope"):
        build_node(state, llm=llm, paths=paths)


def test_build_node_rejects_any_writes_when_plan_scope_is_empty(tmp_path: Path) -> None:
    """Verifies that an empty Dora allowlist means no project writes are permitted."""
    project_root = tmp_path / "project"
    global_agents_dir = tmp_path / "global-agents"
    paths = load_runtime_paths(project_root, global_agents_dir)
    _write_agent(global_agents_dir / "primary" / "Bob the Builder.md", "Build prompt")
    llm = FakeLlm(
        "```json\n"
        '{"status":"BUILD_DONE","ready_to_ship":"no","implementation_summary":"Implemented","modified_files":[],"file_writes":[{"path":"README.md","content":"updated"}],"pipeline":{"tests":"passed","review":"passed","seo":"skipped","accessibility":"skipped","security":"passed","cleanup":"passed","ai_context":"skipped","documentation":"passed"},"blocking_reason":"","non_blocking_findings":[]}\n'
        "```"
    )
    state = RunState(
        user_request="Add runtime tests",
        plan_file="plans/runs/run-abc.md",
        plan_summary="Ready",
        approved=True,
        artifacts={
            "dora_output": {
                "status": "PLAN_READY",
                "plan_file": "plans/runs/run-abc.md",
                "plan_markdown": "# Plan\n",
                "summary": "Ready",
                "requirements": ["A"],
                "files_to_modify": [],
                "complexity": "S",
                "needs_human_approval": True,
                "questions_remaining": [],
            }
        },
    )

    with pytest.raises(ValueError, match="outside the approved plan scope"):
        build_node(state, llm=llm, paths=paths)


@pytest.mark.parametrize(
    ("bob_output", "expected_step", "expected_reason"),
    [
        (
            {
                "status": "BUILD_BLOCKED",
                "ready_to_ship": "no",
                "implementation_summary": "Blocked",
                "modified_files": [],
                "pipeline": {
                    "tests": "blocked",
                    "review": "not_run",
                    "seo": "not_run",
                    "accessibility": "not_run",
                    "security": "not_run",
                    "cleanup": "not_run",
                    "ai_context": "not_run",
                    "documentation": "not_run",
                },
                "blocking_reason": "Need approval",
                "non_blocking_findings": [],
            },
            RunStep.BLOCKED,
            "Need approval",
        ),
        (
            {
                "status": "BUILD_DONE",
                "ready_to_ship": "yes",
                "implementation_summary": "Done",
                "modified_files": [],
                "pipeline": {
                    "tests": "passed",
                    "review": "passed",
                    "seo": "skipped",
                    "accessibility": "skipped",
                    "security": "passed",
                    "cleanup": "passed",
                    "ai_context": "skipped",
                    "documentation": "passed",
                },
                "blocking_reason": "",
                "non_blocking_findings": [],
            },
            RunStep.DONE,
            "",
        ),
    ],
)
def test_review_result_node_routes_from_bob_output(
    bob_output: dict,
    expected_step: RunStep,
    expected_reason: str,
) -> None:
    """Verifies that review routing honors blocked and ready-to-ship outcomes."""
    state = RunState(user_request="Request", artifacts={"bob_output": bob_output})

    result = review_result_node(state)

    assert result["current_step"] == expected_step
    assert result.get("blocked_reason", "") == expected_reason


def test_intake_node_preserves_non_initial_state() -> None:
    """Verifies that resumed runs keep their persisted step instead of being re-derived."""
    state = RunState(user_request="Request", current_step=RunStep.DONE, plan_file="plans/run.md", approved=True)

    result = intake_node(state)

    assert result == {"current_step": RunStep.DONE}
