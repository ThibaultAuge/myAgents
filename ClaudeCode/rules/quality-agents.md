# Quality agent routing

After implementation, inspect the actual changes and route them to the agents whose
expertise is genuinely relevant. Do not invoke agents mechanically when they add no
value. `implementation.md` defines the order these gates run in.

## Signal to agent

| Signal in the diff | Agent | Role |
|---|---|---|
| Code, tests, APIs, or build scripts changed | `dexter` | Writes unit, integration, and API contract tests |
| Code or a non-trivial prompt/workflow changed | `hermione` | Reviews for bugs, performance, maintainability |
| Files that generate HTML | `gatsby` | SEO audit — meta tags, semantic structure, performance signals |
| Files that generate HTML or UI behavior | `timmy` | Accessibility audit against WCAG 2.1 AA |
| Auth, secrets, permissions, external calls, user input, config, dependencies, env vars | `neo` | Security audit |
| Refactor, removal, rename, replaced component | `hancock` | Dead code detection and removal |
| `AGENTS.md`, `CLAUDE.md`, `docs/ai/**/*.md`, `.claude/rules/**`, `.claude/context/**`, `.claude/agents/**`, `.claude/skills/**` | `curator` | AI-facing context documentation |
| README, API reference, user guide, changelog, Javadoc | `otis` | Human-facing documentation |
| Any numeric result, statistic, or unit conversion, at any point | `turing` | Executes Python so the figure is computed, never inferred |

`dexter` writes tests; `hermione` reviews code. They are not interchangeable.

Run `gatsby` before `timmy`, and only when rendered content actually changed — a
backend-only diff triggers neither.

## Shared reporting vocabulary

The audit agents share a vocabulary so their reports stay comparable:

- **Severity** — 🔴 BLOCKING or CRITICAL, 🟠 HIGH (`neo` only), 🟡 WARNING or
  NON-BLOCKING, 🔵 SUGGESTION or INFORMATIONAL
- **Verdict** — `APPROVE`, `APPROVE WITH SUGGESTIONS`, `APPROVE WITH WARNINGS`,
  `REQUEST CHANGES`
- **Skip marker** — ⏭ followed by the reason a gate did not run

`hancock` is the exception: it reuses 🔴/🟡/🔵 for **removal confidence**, not severity.
Its 🔴 means "safe to delete", not "stop". Only `hermione`, `gatsby`, `timmy`, and `neo`
emit pipeline-stopping findings.

Address relevant findings before considering the task complete. A 🔴 severity finding stops
the pipeline; see the blocking behavior section of `implementation.md`.
