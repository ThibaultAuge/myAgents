---
description: Use when creating or editing an agent in `ClaudeCode/agents/` or changing the pipeline rules that call agents.
---

# Claude Code agent files

## Current State
`ClaudeCode/agents/` holds thirteen Claude Code subagents, flat, one Markdown file per agent with YAML frontmatter followed by the prompt. The filename has no spaces and matches the kebab-case `name:` field. They are called from the pipeline in `ClaudeCode/rules/` (`planning.md`, `implementation.md`, `quality-agents.md`).

## Relevant Files
- `ClaudeCode/agents/*.md`
- `ClaudeCode/rules/planning.md`, `ClaudeCode/rules/implementation.md`, `ClaudeCode/rules/quality-agents.md`

## Usage
- Preserve the frontmatter delimiters (`---` at start and end) and keep existing keys unless intentionally changing them.
- **No orphan agents.** Every agent in `ClaudeCode/agents/` must be referenced at least once from `ClaudeCode/rules/`, otherwise it can never be triggered and is dead weight. `Turing` was exactly that under OpenCode: listed in the README, called by nobody.
- Keep the planning/implementation boundary intact: `planning.md` plans and stops at human approval; `implementation.md` executes and orchestrates the quality gates.
- The implementation pipeline is conditional and gated: classify changed files and risks first, call only the applicable agents in fixed order, and report skipped gates with reasons. When changing it, update the ordered pipeline, the change classification, the post-agent revalidation, the final summary, and the behavior rules together so they cannot disagree.
- Reclassify and re-run the applicable gates whenever an agent such as `hancock` or `otis` edits source, tests, config, dependencies, generated UI, permissions, or agent behavior after earlier gates passed.

Verification checks for `ClaudeCode/agents/`: frontmatter parses; `name:` is kebab-case and equals the filename; `model` is one of `sonnet`, `opus`, `haiku`, `fable`, `inherit`; `tools` lists real Claude Code tool names; every referenced agent exists; every agent is cited from `rules/`.

## Notes
- `gatsby`, `timmy`, `otis`, and `turing` intentionally use `model: haiku` to reduce checklist, editorial, and scripted-computation cost (the intent `opencode/big-pickle` served). Do not create fallback duplicate agents; if the cheaper model is inadequate, a human will change it.
- `gatsby` and `timmy` are read-only web auditors with no `Bash`. Call them only for HTML-generating web/UI changes, never for backend-only, docs-only, or agent-only changes.
- Do not grant internet tools casually. `oracle` is the only agent with `WebSearch` and `WebFetch`. Its purpose is not to monopolise web access (the main session has those tools too) but to read external content in an isolated context so untrusted page content never enters the main conversation.
- `hancock` can write confirmed cleanup and logging changes, but must request exact-path confirmation before deletions and return exact modified or deleted paths for the revalidation loop.
- `otis`: Javadoc and source edits require an explicit Javadoc request; otherwise its documentation updates stay in human-facing Markdown.
