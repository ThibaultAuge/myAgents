# Gatekeeper Runtime

Install this package globally on the machine that will run Gatekeeper. It is the LangGraph-based orchestrator for shared agents plus per-project state.

It loads:
- global agents from this repository's `agents/`
- optional project overrides from `.gatekeeper/agents/`
- project run state from `.gatekeeper/runs/`

## Install

From the repository root:

```bash
pip install ./runtime
```

## Current execution mode

The runtime currently ships a **direct-LLM runner** plus the LangGraph state machine.

- It can orchestrate state, persistence, approvals, and structured contracts.
- It can directly execute **runtime-compatible agents that do not require tools**.
- In direct-LLM mode, the runtime itself writes plan artifacts and applies explicit `file_writes` returned by runtime-compatible agents.
- For tool-heavy OpenCode-style agents such as the current shared `Dora` and `Bob`, you must either:
  - provide runtime-compatible overrides under `.gatekeeper/agents/`, or
  - add a future tool-runner adapter.

This avoids false claims about files being written or pipelines being executed when no real tool layer exists.

The `project-template/` directory includes starter runtime-compatible overrides for `Dora the Explorer` and `Bob the Builder` under `.gatekeeper/agents/primary/`.

## Commands

```bash
gatekeeper-runtime start --project /path/to/project --request "..."
gatekeeper-runtime resume --project /path/to/project --run-id run-example-001
gatekeeper-runtime approve --project /path/to/project --run-id run-example-001
```

## Global vs project split

### Global install on the PC
- `runtime/` package
- `agents/` prompt library in this repo

Set the shared global agent path once via:
- `GATEKEEPER_GLOBAL_AGENTS_DIR`, or
- each project's `.gatekeeper/gatekeeper.yaml`

### Copied into each project
- `.gatekeeper/gatekeeper.yaml`
- `.gatekeeper/agents/` for project-specific overrides, including starter direct-LLM Dora/Bob overrides in the template
- `.gatekeeper/runs/` for persisted run state
- `plans/` and `plans/runs/` for plan artifacts expected by the agents

## Testing

The runtime package includes a pytest suite under `runtime/tests/`.

```bash
pytest runtime/tests
```
