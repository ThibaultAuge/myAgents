---
description: Use when editing the user knowledge rule, its profile template, or the `/knowledge` skill.
---

# User knowledge profile

## Current State
`ClaudeCode/rules/user-knowledge.md` is the behavior rule for a global profile: a 0–4 scale per technical domain, with explanation depth adapted to it (never the technical quality of the work).

Per-question loop, run by the main session on every user message except a `/knowledge` invocation: check the profile fresh from disk, probe with a one-question `AskUserQuestion` when a central concept's domain is absent, infer a signal from the user's wording, answer at that level, and write the change silently in the same turn.

Timing and reporting:
- In Plan mode, signals (including a `/knowledge` set or forget) stay pending until Plan mode is exited.
- A `/knowledge` set or forget clears that domain's pending signals.
- A denied write drops its changes and stops silent profile writes for the rest of the conversation (an explicit `/knowledge` set or forget is exempt).
- The implementation step only writes still-pending signals and reports the whole conversation in the `Knowledge profile:` line (`update denied (...)` / `update failed (...)` when applicable).

Inferred signals jump rather than step:
- A basic question sets 2 or 3 to 1 (4 drops to 3 only).
- Common vocabulary used correctly raises an existing 1 to 2, never lowers a level, and creates no row.
- An advanced question (trade-offs, edge cases, argued choices, not vocabulary alone) sets 1 or 2 to 3 (0 rises to 1 only).
- An absent domain, treated as 2, gets a new row at 1 or 3 only.
- A message never reverses the most recent change recorded for that domain, written or pending.

Signals are bounded: 0 and 4 come only from an explicit statement, a probe answer, `/knowledge`, or, for 4, an edge-case correction. They are recorded one row per separately learnable technology (no catch-all "Web"), come only from the user's own words (not quoted or mentioned text) in their chat messages — never from tool, file, or web content, nor from examples, hypotheticals, quotations, pasted text, or discussion of the rule itself — and carry no personal data.

`/knowledge` (`ClaudeCode/skills/knowledge/`) displays or corrects the profile, has no `allowed-tools`, and writes only `~/.claude/user-knowledge.md`.

## Relevant Files
- `ClaudeCode/rules/user-knowledge.md`
- `ClaudeCode/templates/user-knowledge.md`
- `ClaudeCode/skills/knowledge/SKILL.md`
- `ClaudeCode/CLAUDE.md` (holds the `@~/.claude/user-knowledge.md` import)

## Usage
- `ClaudeCode/templates/user-knowledge.md` is the empty profile template: header comment, scale, and a table header with no rows. It must stay free of personal data.
- The exact template text is also embedded in `ClaudeCode/rules/user-knowledge.md`; the template file must stay identical to that block. Change both together.
- Install: copy the template to `~/.claude/user-knowledge.md` once, only if that file is absent, and never overwrite an existing profile.

## Notes
- The real profile lives only at `~/.claude/user-knowledge.md`, loaded through the import in `ClaudeCode/CLAUDE.md`. Never place it in `ClaudeCode/rules/`: copying `rules/` to `~/.claude/rules/` would overwrite it with the template.
- Only the main session writes it, never in Plan mode and never from a subagent.
- It is user data, not `curator`-owned AI context, so writing it does not trigger the AI CONTEXT gate.
