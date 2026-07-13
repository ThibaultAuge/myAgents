# Repository Instructions

## Scope
- This repo stores OpenCode agent definitions plus a Python Gatekeeper runtime package and a per-project template for project-local assets.
- Agent files are Markdown with YAML frontmatter followed by the agent prompt.
- The `runtime/` package has its own pytest suite under `runtime/tests/`; there is still no broader repo-wide CI configuration in the current tree.

## Layout
- `agents/` contains the OpenCode core so it stays isolated from project-level files such as `README.md`.
- `agents/primary/` contains primary-mode orchestrators such as `Gatekeeper.md`, `Dora the Explorer.md`, and `Bob the Builder.md`.
- `agents/subagent/` contains callable subagents such as `The Curator.md`, `Dexter.md`, `Hermione.md`, `Neo.md`, and `Oracle.md`.
- `runtime/` contains the shared Python LangGraph runtime package, CLI, storage/state/config modules, and pytest coverage for that package.
- `project-template/` contains the project-local `.gatekeeper/` and `plans/` assets that get copied into consumer projects, including runtime-compatible Dora/Bob overrides.
- Filenames include spaces and must match the agent names used in prompts, for example `@Bob the Builder` and `@Samuel Morse`.
- Runtime state persists under `.gatekeeper/runs/`; planning artifacts live under `plans/`, and plan-run artifacts live under `plans/runs/`.

## Editing Agent Files
- Preserve the frontmatter delimiter format (`---` at start and end) and keep existing YAML keys such as `description`, `mode`, `tools`, `model`, and `temperature` unless intentionally changing them.
- Do not grant internet tools casually. Most agents explicitly state they have no internet; `Oracle.md` is the only current agent with `websearch: true` and `webfetch: true`.
- Keep a clear separation between the shared global runtime/agent library (`runtime/`, `agents/`) and project-local copied assets (`project-template/.gatekeeper/`, `project-template/plans/`).
- Use `Gatekeeper.md` as the default primary entry point for new structured workflow requests; it owns run state, approval tracking, and delegation to Dora/Bob.
- Keep primary/subagent boundaries intact: `Gatekeeper.md` is the workflow orchestrator, `Dora the Explorer.md` plans only, and `Bob the Builder.md` implements and orchestrates the internal quality pipeline.
- Gatekeeper's V1 run state machine is `INTAKE`, `CLARIFY`, `PLAN`, `WAITING_APPROVAL`, `BUILD`, `REVIEW_RESULT`, `DONE`, `BLOCKED`; keep any related guidance synchronized when changing that workflow.
- Gatekeeper does not replace Bob's internal quality pipeline; approved implementation still flows through Bob once Gatekeeper delegates it.
- Dora may write plan artifacts under `./plans/`, but it must not route implementation directly to Bob; approved work returns to Gatekeeper for approval tracking and delegation.
- Shared OpenCode-style Dora/Bob prompts remain tool-heavy. Direct-LLM runtime execution should use the runtime-compatible project-local overrides unless a future tool-runner adapter is added.
- The runtime loads shared agents from a configured global library path and supports project-local overrides; preserve that override model when changing agent-loading guidance.
- When editing Gatekeeper, Dora, Bob, or runtime file-writing guidance, preserve the sanitization, run ID validation, plan-file validation, allowlisted file writes, and directory-boundary rules around `.gatekeeper/runs/`, `plans/`, and `plans/runs/`.
- If changing Bob's pipeline, update both the ordered `Pipeline` section and the later `Behavior Rules` / integration text so they do not disagree.
- `The Curator.md` is the only agent that should update AI-facing current-state documentation such as `AGENTS.md`, `docs/ia/**/*.md`, `docs/ai/**/*.md`, or agent-context Markdown files. `Otis.md` remains responsible for human-facing documentation only.

## Verification
- Use `pytest` under `runtime/` for automated verification of the Python runtime package.
- For prompt changes, verify manually by reading the changed Markdown for YAML validity, broken `@Agent` references, and contradictions with related agents.

## Known Gotchas
- `Gatsby.md` and `Timmy.md` mention requesting current guidance via `@Alexandria`, but this repo defines `Oracle.md` as the only internet-enabled research agent.
