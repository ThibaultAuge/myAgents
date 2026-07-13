from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_project_settings
from .contracts import RunStep
from .graph import build_graph
from .llm import build_default_llm
from .state import RunState
from .storage import load_run_state, save_run_state


def start_run(args: argparse.Namespace) -> None:
    settings = load_project_settings(args.project, args.global_agents_dir)
    state = RunState(user_request=args.request)
    app = build_graph(build_default_llm(settings.models.provider, settings.models.model), settings.paths)
    result = app.invoke(state)
    final_state = RunState.model_validate(result)
    print(final_state.model_dump_json(indent=2))


def resume_run(args: argparse.Namespace) -> None:
    settings = load_project_settings(args.project, args.global_agents_dir)
    state = load_run_state(settings.paths.runs_dir, args.run_id)
    app = build_graph(build_default_llm(settings.models.provider, settings.models.model), settings.paths)
    result = app.invoke(state)
    final_state = RunState.model_validate(result)
    print(final_state.model_dump_json(indent=2))


def approve_run(args: argparse.Namespace) -> None:
    settings = load_project_settings(args.project, args.global_agents_dir)
    state = load_run_state(settings.paths.runs_dir, args.run_id)
    if state.current_step != RunStep.WAITING_APPROVAL:
        raise ValueError(f"Run {args.run_id} is not waiting for approval; current step is {state.current_step}.")
    state.approved = True
    state.current_step = RunStep.BUILD
    save_run_state(settings.paths.runs_dir, state)
    print(f"Approved {args.run_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gatekeeper-runtime")
    parser.add_argument("--global-agents-dir", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--project", required=True, type=Path)
    start.add_argument("--request", required=True)
    start.set_defaults(func=start_run)

    resume = subparsers.add_parser("resume")
    resume.add_argument("--project", required=True, type=Path)
    resume.add_argument("--run-id", required=True)
    resume.set_defaults(func=resume_run)

    approve = subparsers.add_parser("approve")
    approve.add_argument("--project", required=True, type=Path)
    approve.add_argument("--run-id", required=True)
    approve.set_defaults(func=approve_run)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
