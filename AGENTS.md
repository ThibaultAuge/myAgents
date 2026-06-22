# Repository Instructions

## Scope
- This repo stores OpenCode agent definitions only; there is no app code, package manifest, CI, or test runner in the current tree.
- Agent files are Markdown with YAML frontmatter followed by the agent prompt.

## Layout
- `agents/` contains the OpenCode core so it stays isolated from project-level files such as `README.md`.
- `agents/primary/` contains primary-mode orchestrators such as `Dora the Explorer.md` and `Bob the Builder.md`.
- `agents/subagent/` contains callable subagents such as `Dexter.md`, `Hermione.md`, `Neo.md`, and `Oracle.md`.
- Filenames include spaces and must match the agent names used in prompts, for example `@Bob the Builder` and `@Samuel Morse`.

## Editing Agent Files
- Preserve the frontmatter delimiter format (`---` at start and end) and keep existing YAML keys such as `description`, `mode`, `tools`, `model`, and `temperature` unless intentionally changing them.
- Do not grant internet tools casually. Most agents explicitly state they have no internet; `Oracle.md` is the only current agent with `websearch: true` and `webfetch: true`.
- Keep primary/subagent boundaries intact: `Dora the Explorer.md` plans only, while `Bob the Builder.md` implements and orchestrates the quality pipeline.
- If changing Bob's pipeline, update both the ordered `Pipeline` section and the later `Behavior Rules` / integration text so they do not disagree.

## Verification
- No repo-local automated checks exist. For prompt changes, verify manually by reading the changed Markdown for YAML validity, broken `@Agent` references, and contradictions with related agents.

## Known Gotchas
- `Dora the Explorer.md` has `write: false` but instructs Dora to save plans under `./plans/`; do not rely on that behavior without resolving the permission mismatch.
- `Gatsby.md` and `Timmy.md` mention requesting current guidance via `@Alexandria`, but this repo defines `Oracle.md` as the only internet-enabled research agent.
