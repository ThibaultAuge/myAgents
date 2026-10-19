---
description: Use when editing the user knowledge rule, its profile template, or the `/knowledge` skill.
---

# User knowledge profile

## Current State
A global per-user profile records how well the user knows each technical domain. Its behavior is defined in the files below; read them rather than a summary.

## Relevant Files
- `ClaudeCode/rules/user-knowledge.md` — always loaded: scale, per-question loop, probe conditions, update bounds, write timing, reporting format, and how a `/knowledge` set or forget interacts with pending signals, Plan mode, and a denied write.
- `ClaudeCode/context/user-knowledge-details.md` — on demand: probe form and answer scoring, and the profile template with its sync requirement against `ClaudeCode/templates/user-knowledge.md`.
- `ClaudeCode/templates/user-knowledge.md` — the empty profile template; its header comment says how to install it.
- `ClaudeCode/skills/knowledge/SKILL.md` — `/knowledge` commands and what the skill does while it runs. Its no-orphan citation is covered in `docs/ai/skill-tool-grants.md`.
- `ClaudeCode/CLAUDE.md` — holds the `@~/.claude/user-knowledge.md` import.

## Usage
- Each fact has one home among these files (single-source rule in `ClaudeCode/agents/curator.md`). Behavior the main session applies on every message goes in the rule; detail needed only when probing or creating the file goes in the context file; behavior needed only while `/knowledge` runs goes in the skill. The other files point to it.

## Notes
- The rule forbids keeping the profile under `~/.claude/rules/`. The repo-side reason: installing means copying `ClaudeCode/rules/` to `~/.claude/rules/`, which would overwrite a profile kept there.
- `ClaudeCode/templates/user-knowledge.md` must stay free of personal data.
