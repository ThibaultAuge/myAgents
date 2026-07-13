# Repository Instructions

## Scope
- This repo stores OpenCode agent definitions only; there is no app code, package manifest, CI, or test runner in the current tree.
- Agent files are Markdown with YAML frontmatter followed by the agent prompt.

## Layout
- `agents/` contains the OpenCode core so it stays isolated from project-level files such as `README.md`.
- `agents/primary/` contains primary-mode orchestrators such as `Dora the Explorer.md` and `Bob the Builder.md`.
- `agents/subagent/` contains callable subagents such as `The Curator.md`, `Dexter.md`, `Hermione.md`, `Neo.md`, and `Oracle.md`.
- Filenames include spaces and must match the agent names used in prompts, for example `@Bob the Builder` and `@Samuel Morse`.

## Editing Agent Files
- Preserve the frontmatter delimiter format (`---` at start and end) and keep existing YAML keys such as `description`, `mode`, `tools`, `model`, and `temperature` unless intentionally changing them.
- `Gatsby.md`, `Timmy.md`, and `Otis.md` intentionally use `model: opencode/big-pickle` by default to reduce checklist/editorial agent cost. Do not create fallback duplicate agents for these; if the free model is inadequate or unavailable, a human will manually change the model.
- `Gatsby.md` and `Timmy.md` are read-only web auditors with `bash: false`; Bob should only call them for HTML-generating web/UI changes, not backend-only, docs-only, or agent-only changes.
- Do not grant internet tools casually. Most agents explicitly state they have no internet; `Oracle.md` is the only current agent with `websearch: true` and `webfetch: true`.
- Keep primary/subagent boundaries intact: `Dora the Explorer.md` plans only, while `Bob the Builder.md` implements and orchestrates the quality pipeline.
- `Dora the Explorer.md` has `write: true` and `edit: false`; her prompt constrains writes to plan files under `./plans/` only.
- `Bob the Builder.md` uses a conditional gated pipeline: classify changed files/risks first, call only applicable subagents in fixed order, and report skipped steps with reasons. If changing Bob's pipeline, update the ordered `Pipeline`, change-classification, post-agent revalidation, final summary, and `Behavior Rules` text so they do not disagree.
- Bob must reclassify and re-run applicable gates when a subagent such as `Hancock.md` or `Otis.md` edits source, tests, config, dependencies, generated UI, permissions, or agent behavior after earlier checks have passed.
- `Hancock.md` can write confirmed cleanup/logging changes, but must request exact-path confirmation before deletions and return exact modified/deleted paths for Bob's revalidation loop.
- `Otis.md` can write/edit human-facing docs and keeps `model: opencode/big-pickle`; Javadoc/source edits are only for explicit Javadoc requests, otherwise documentation updates should stay in human-facing Markdown.
- `The Curator.md` is the only agent that should update AI-facing current-state documentation such as `AGENTS.md`, `docs/ia/**/*.md`, `docs/ai/**/*.md`, or agent-context Markdown files. `Otis.md` remains responsible for human-facing documentation only.

## Verification
- No repo-local automated checks exist. For prompt changes, verify manually by reading the changed Markdown for YAML validity, broken `@Agent` references, and contradictions with related agents.
- OpenCode loads agent frontmatter at startup. After changing an agent `model` or other frontmatter, quit and restart OpenCode before expecting the new configuration to take effect.

## Known Gotchas
- Agent frontmatter currently uses a `tools:` map for permissions. OpenCode may prefer `permission:` for enforcement in some configurations; do not silently rewrite all agents, but treat this as a security/configuration concern for future dedicated review.
