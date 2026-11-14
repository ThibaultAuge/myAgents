---
description: Use when creating or editing an agent in `ClaudeCode/agents/`, or changing the pipeline rules or `ClaudeCode/context/` files that call agents or skills.
---

# Claude Code agent files

## Current State
`ClaudeCode/agents/` holds thirteen Claude Code subagents, flat, one Markdown file per agent with YAML frontmatter followed by the prompt. The filename has no spaces and matches the kebab-case `name:` field. They are called from the pipeline in `ClaudeCode/rules/` (`planning.md`, `implementation.md`, `quality-agents.md`).

## Relevant Files
- `ClaudeCode/agents/*.md`
- `ClaudeCode/rules/planning.md`, `ClaudeCode/rules/implementation.md`, `ClaudeCode/rules/quality-agents.md` (always loaded)
- `ClaudeCode/context/plan-template.md`, `ClaudeCode/context/pipeline-reports.md` (on demand; each file's `description:` says when the rules read it)

## Usage
- Preserve the frontmatter delimiters (`---` at start and end) and keep existing keys unless intentionally changing them.
- **No orphan agents.** Every agent in `ClaudeCode/agents/` must be referenced at least once from `ClaudeCode/rules/`, otherwise it can never be triggered and is dead weight. `Turing` was exactly that under OpenCode: listed in the README, called by nobody. An agent named only in a `ClaudeCode/context/` file is not cited from `rules/` and counts as an orphan.
- Skills have their own no-orphan rule: see `docs/ai/skill-tool-grants.md`.
- Keep the planning/implementation boundary intact when editing either rule: `planning.md` stops at human approval, `implementation.md` executes.
- When changing the implementation pipeline, update together, so they cannot disagree: the three gate waves (Wave 1 TEST; Wave 2 read-only audits in parallel; Wave 3 editing agents in sequence), the contract-and-lots section (contract commit only for worktree lots, lot guard, worktree merge, out-of-list revert), the change classification, the blocking behavior, the documentation ownership (plan-listed AI-context files belong to their lot's owner), the post-agent revalidation, and the behavior rules in `implementation.md`; the routing table in `quality-agents.md`, which defers ordering to those waves; the per-agent inputs (including the `general-purpose` lot subagent brief) and the final summary template (including its Work split line) in `ClaudeCode/context/pipeline-reports.md`; the Work Breakdown section and delegation guide in `ClaudeCode/context/plan-template.md`. The opening sentences of `implementation.md` and `quality-agents.md` reserve the pipeline to the main session; keep them, since subagents load these rules too.
- When changing planning delegation, keep Phase 1b (parallel discovery) in `planning.md` pointing to the Phase 3 table instead of repeating its rows; that table stays the single source for which agent handles what. `Explore` and `general-purpose` are built-in subagent types, not files in `ClaudeCode/agents/`, so the no-orphan rule does not apply to them.
- Splitting between `ClaudeCode/rules/` and `ClaudeCode/context/` follows the tier convention in `ClaudeCode/agents/curator.md` (Context tiers).

Verification checks for `ClaudeCode/agents/`: frontmatter parses; `name:` is kebab-case and equals the filename; `model` is one of `sonnet`, `opus`, `haiku`, `fable`, `inherit`; `tools` lists real Claude Code tool names; every referenced agent exists; every agent is cited from `rules/`.

## Notes
- `gatsby`, `timmy`, `otis`, and `turing` intentionally use `model: haiku` to reduce checklist, editorial, and scripted-computation cost (the intent `opencode/big-pickle` served). Do not create fallback duplicate agents; if the cheaper model is inadequate, a human will change it.
- `gatsby` and `timmy` are read-only web auditors with no `Bash`. When they run is set by the web gating in `implementation.md`.
- Do not grant internet tools casually. `oracle` is the only agent with `WebSearch` and `WebFetch`; why it exists is stated in Phase 3 of `planning.md`.
- `hancock`'s confirmation and reporting contract is in `ClaudeCode/agents/hancock.md`; revalidation after any agent edit is in `implementation.md`.
- `otis`'s Javadoc scope is in `ClaudeCode/agents/otis.md`.
