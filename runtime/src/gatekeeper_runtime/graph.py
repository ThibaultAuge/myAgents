from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from .agents import AgentDefinition, load_agent
from .config import RuntimePaths
from .contracts import BobOutput, DoraOutput, RunStep
from .state import RunState
from .storage import save_run_state


JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def extract_json_block(text: str) -> dict[str, Any]:
    match = JSON_BLOCK_RE.search(text)
    if not match:
        raise ValueError("Expected a fenced ```json block in agent output.")
    return json.loads(match.group(1))


def sanitize_token(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9-]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered or "run"


def invoke_agent(llm, prompt: str, task: str) -> str:
    response = llm.invoke(f"{prompt}\n\n## Runtime Task\n{task}")
    return getattr(response, "content", str(response))


def normalize_plan_file(plan_file: str, *, paths: RuntimePaths) -> str:
    candidate = Path(plan_file)
    if candidate.is_absolute():
        raise ValueError(f"Plan file must be project-relative and stay under plans_dir: {plan_file}")

    resolved = (paths.project_root / candidate).resolve()
    plans_dir_resolved = paths.plans_dir.resolve()
    try:
        resolved.relative_to(plans_dir_resolved)
    except ValueError as exc:
        raise ValueError(f"Plan file escaped plans_dir: {plan_file}") from exc

    return resolved.relative_to(paths.project_root).as_posix()


def normalize_project_relative(project_root: Path, relative_path: str, *, forbidden_top_level: set[str] | None = None) -> str:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError(f"Project file write must be relative: {relative_path}")

    if forbidden_top_level and candidate.parts and candidate.parts[0] in forbidden_top_level:
        raise ValueError(f"Project file write targets a forbidden top-level path: {relative_path}")

    resolved = (project_root / candidate).resolve()
    project_root_resolved = project_root.resolve()
    try:
        resolved.relative_to(project_root_resolved)
    except ValueError as exc:
        raise ValueError(f"Project file write escaped project root: {relative_path}") from exc

    return resolved.relative_to(project_root_resolved).as_posix()


def write_project_text(project_root: Path, relative_path: str, content: str, *, forbidden_top_level: set[str] | None = None) -> str:
    normalized = normalize_project_relative(
        project_root,
        relative_path,
        forbidden_top_level=forbidden_top_level,
    )
    resolved = (project_root / normalized).resolve()

    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")
    return normalized


def ensure_direct_llm_compatible(agent: AgentDefinition) -> None:
    tools = agent.frontmatter.get("tools", {}) or {}
    unsupported = sorted(key for key, enabled in tools.items() if enabled)
    if unsupported:
        raise RuntimeError(
            "Direct LLM mode cannot execute tool-enabled agent "
            f"{agent.name!r}. Unsupported tools: {', '.join(unsupported)}. "
            "Provide a runtime-compatible override in .gatekeeper/agents/ or add a real tool runner adapter."
        )


def intake_node(state: RunState) -> dict[str, Any]:
    if state.current_step != RunStep.INTAKE:
        return {"current_step": state.current_step}
    if state.plan_file and state.approved:
        return {"current_step": RunStep.BUILD}
    if state.plan_file:
        return {"current_step": RunStep.WAITING_APPROVAL}
    return {"current_step": RunStep.PLAN}


def plan_node(state: RunState, *, llm, paths: RuntimePaths) -> dict[str, Any]:
    agent = load_agent(paths, "primary/Dora the Explorer.md")
    ensure_direct_llm_compatible(agent)
    task = (
        "Produce a plan and finish with exactly one fenced ```json block matching this schema:\n"
        "{status:'PLAN_READY', plan_file:string, plan_markdown:string, summary:string, requirements:string[], files_to_modify:string[], complexity:'XS|S|M|L|XL', needs_human_approval:true, questions_remaining:string[]}\n"
        f"Use run token {state.run_id}. User request: {state.user_request}"
    )
    output = invoke_agent(llm, agent.prompt, task)
    parsed = DoraOutput.model_validate(extract_json_block(output))
    if parsed.questions_remaining:
        raise ValueError("PLAN_READY output cannot include questions_remaining.")
    plan_file = normalize_plan_file(parsed.plan_file, paths=paths)
    if state.run_id not in plan_file:
        raise ValueError(f"Plan file must include the run_id token {state.run_id!r}: {plan_file}")
    write_project_text(paths.project_root, plan_file, parsed.plan_markdown)
    return {
        "current_step": RunStep.WAITING_APPROVAL,
        "plan_file": plan_file,
        "plan_summary": parsed.summary,
        "artifacts": {
            **state.artifacts,
            "dora_output": parsed.model_dump(),
            "dora_raw": output,
            "written_plan_file": plan_file,
        },
    }


def approval_node(state: RunState) -> dict[str, Any]:
    if state.approved:
        return {"current_step": RunStep.BUILD}
    return {"current_step": RunStep.WAITING_APPROVAL}


def build_node(state: RunState, *, llm, paths: RuntimePaths) -> dict[str, Any]:
    agent = load_agent(paths, "primary/Bob the Builder.md")
    ensure_direct_llm_compatible(agent)
    task = (
        "Implement the approved plan. Finish with exactly one fenced ```json block matching this schema:\n"
        "{status:'BUILD_DONE|BUILD_BLOCKED', ready_to_ship:'yes|no', implementation_summary:string, modified_files:string[], file_writes:[{path:string, content:string}], pipeline:{tests:'passed|failed|blocked|skipped|not_run', review:'passed|failed|blocked|skipped|not_run', seo:'passed|failed|blocked|skipped|not_run', accessibility:'passed|failed|blocked|skipped|not_run', security:'passed|failed|blocked|skipped|not_run', cleanup:'passed|failed|blocked|skipped|not_run', ai_context:'passed|failed|blocked|skipped|not_run', documentation:'passed|failed|blocked|skipped|not_run'}, blocking_reason:string, non_blocking_findings:string[]}\n"
        f"Plan file: {state.plan_file}\nPlan summary: {state.plan_summary}\nHuman approval: explicit"
    )
    output = invoke_agent(llm, agent.prompt, task)
    parsed = BobOutput.model_validate(extract_json_block(output))
    if parsed.status == "BUILD_BLOCKED" and parsed.file_writes:
        raise ValueError("BUILD_BLOCKED output cannot include file_writes.")

    applied_files = []
    if parsed.status == "BUILD_DONE":
        dora_output = DoraOutput.model_validate(state.artifacts.get("dora_output", {}))
        allowed_paths = {
            normalize_project_relative(paths.project_root, file_path, forbidden_top_level={".gatekeeper"})
            for file_path in dora_output.files_to_modify
        }
        proposed_writes = [
            (
                normalize_project_relative(paths.project_root, file_write.path, forbidden_top_level={".gatekeeper"}),
                file_write.content,
            )
            for file_write in parsed.file_writes
        ]
        for proposed_path, _ in proposed_writes:
            if proposed_path not in allowed_paths:
                raise ValueError(
                    f"Applied file {proposed_path!r} is outside the approved plan scope: {sorted(allowed_paths)}"
                )
        applied_files = [
            write_project_text(paths.project_root, proposed_path, content, forbidden_top_level={".gatekeeper"})
            for proposed_path, content in proposed_writes
        ]
    return {
        "current_step": RunStep.REVIEW_RESULT,
        "approved": False,
        "build_summary": parsed.implementation_summary,
        "modified_files": parsed.modified_files or applied_files,
        "blocked_reason": parsed.blocking_reason,
        "artifacts": {
            **state.artifacts,
            "bob_output": parsed.model_dump(),
            "bob_raw": output,
        },
    }


def review_result_node(state: RunState) -> dict[str, Any]:
    bob_output = BobOutput.model_validate(state.artifacts["bob_output"])
    if bob_output.status == "BUILD_BLOCKED":
        return {"current_step": RunStep.BLOCKED, "blocked_reason": bob_output.blocking_reason}
    if bob_output.ready_to_ship == "yes":
        return {"current_step": RunStep.DONE}
    return {"current_step": RunStep.WAITING_APPROVAL, "approved": False}


def persist_node(state: RunState, *, paths: RuntimePaths) -> dict[str, Any]:
    save_run_state(paths.runs_dir, state)
    return {}


def route_after_intake(state: RunState) -> str:
    return state.current_step.value


def route_after_approval(state: RunState) -> str:
    return state.current_step.value


def route_after_review(state: RunState) -> str:
    return state.current_step.value


def build_graph(llm, paths: RuntimePaths):
    graph = StateGraph(RunState)

    graph.add_node("intake", intake_node)
    graph.add_node("plan", lambda state: plan_node(state, llm=llm, paths=paths))
    graph.add_node("approval", approval_node)
    graph.add_node("build", lambda state: build_node(state, llm=llm, paths=paths))
    graph.add_node("review_result", review_result_node)
    graph.add_node("persist", lambda state: persist_node(state, paths=paths))

    graph.add_edge(START, "intake")
    graph.add_conditional_edges(
        "intake",
        route_after_intake,
        {
            RunStep.INTAKE.value: "intake",
            RunStep.PLAN.value: "plan",
            RunStep.WAITING_APPROVAL.value: "approval",
            RunStep.BUILD.value: "build",
            RunStep.REVIEW_RESULT.value: "review_result",
            RunStep.DONE.value: "persist",
            RunStep.BLOCKED.value: "persist",
        },
    )
    graph.add_edge("plan", "persist")
    graph.add_edge("persist", END)
    graph.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            RunStep.WAITING_APPROVAL.value: "persist",
            RunStep.BUILD.value: "build",
        },
    )
    graph.add_edge("build", "review_result")
    graph.add_conditional_edges(
        "review_result",
        route_after_review,
        {
            RunStep.DONE.value: "persist",
            RunStep.BLOCKED.value: "persist",
            RunStep.WAITING_APPROVAL.value: "persist",
        },
    )
    return graph.compile()
