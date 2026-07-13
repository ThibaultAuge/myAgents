# Project Template for Gatekeeper Runtime

Copy this template into each project that will be orchestrated by the global Gatekeeper runtime.

This template holds project-local files only. It does not replace the shared global agent library or the globally installed runtime package.

## What stays global on the PC

- the Python package under `runtime/`
- the shared agent library under `agents/`

## What gets copied into each project

- `.gatekeeper/gatekeeper.yaml`
- `.gatekeeper/agents/` for local prompt overrides
- `.gatekeeper/runs/` for persisted JSON run state
- `plans/` and `plans/runs/` for plan artifacts and run-facing markdown files

## Included runtime-compatible overrides

Direct-LLM mode uses runtime-compatible agent definitions. This template includes starter overrides for:

- `.gatekeeper/agents/primary/Dora the Explorer.md`
- `.gatekeeper/agents/primary/Bob the Builder.md`

## Important

The first runtime mode is **direct LLM**. The shared prompts remain the source of truth for the global library, but agents that need runtime-compatible behavior should be overridden locally until a dedicated tool-runner adapter exists.

Runtime state persists in `.gatekeeper/runs/`. Planning artifacts live in `plans/` and `plans/runs/`.

## Recommended project layout

```text
your-project/
├─ .gatekeeper/
│  ├─ gatekeeper.yaml
│  ├─ agents/
│  └─ runs/
└─ plans/
   └─ runs/
```
