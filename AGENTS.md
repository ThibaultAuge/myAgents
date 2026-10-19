# Repository Instructions

## Scope
- Agent definitions and Claude Code skills only: no app code, package manifest, CI, or test runner. Agent and skill files are Markdown with YAML frontmatter followed by the prompt.
- `OpenCode/` is the original, still-functional OpenCode set, frozen as reference. `ClaudeCode/` is the active Claude Code configuration, staged here and copied to `~/.claude/`.

## Layout
- `OpenCode/agents/primary/`, `OpenCode/agents/subagent/` — OpenCode orchestrators and twelve subagents.
- `ClaudeCode/agents/` — thirteen subagents, one kebab-case file each.
- `ClaudeCode/rules/` — `planning.md`, `implementation.md`, `quality-agents.md` (orchestration and quality gates), `user-knowledge.md` (user knowledge profile rule).
- `ClaudeCode/skills/` — one folder per skill with a `SKILL.md`: `jira-comment/`, `knowledge/`.
- `ClaudeCode/templates/` — files copied once to `~/.claude/` and never overwritten afterwards.
- `ClaudeCode/CLAUDE.md` — staged copy of `~/.claude/CLAUDE.md`: workflow instructions plus the profile import. Not a repo-local readme.
- `docs/ai/` — on-demand AI context (index below). `docs/` otherwise holds repository imagery, including `overview.png` linked from `README.md`.
- `plans/` — generated plans, `plan-<feature>-<date>.md`, written per `ClaudeCode/rules/planning.md`.
- `project-template/`, `runtime/` — empty scaffolding.

## Invariants
- Every committed artifact is written in English.
- `curator` is the only agent that updates AI-facing current-state docs: `AGENTS.md`, `CLAUDE.md`, `docs/ai/**/*.md`, `.claude/rules/**`, `.claude/agents/**`, `.claude/skills/**`. `otis` writes human-facing docs only.
- The real profile `~/.claude/user-knowledge.md` is personal: never commit it.
- `ClaudeCode/agents/`, `rules/`, `skills/`, and `CLAUDE.md` are inert until copied to `~/.claude/`; editing them here changes nothing until then. Both runtimes load agent frontmatter at startup: after changing a `model` or other frontmatter, restart the tool.
- No repo-local automated checks exist. Verify prompt changes by reading the changed Markdown for YAML validity, broken agent references, and contradictions with related agents.

## AI context index
- `docs/ai/agent-files.md` — Use when creating or editing an agent in `ClaudeCode/agents/` or changing the pipeline rules that call agents.
- `docs/ai/skill-tool-grants.md` — Use when creating or editing a skill in `ClaudeCode/skills/`, especially its `allowed-tools` frontmatter.
- `docs/ai/user-knowledge-profile.md` — Use when editing the user knowledge rule, its profile template, or the `/knowledge` skill.
- `docs/ai/opencode-conversion.md` — Use when porting, comparing, or referencing an OpenCode agent or orchestrator against its Claude Code counterpart.

Human documentation: `README.md` and `docs/`.
