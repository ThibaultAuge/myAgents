# My OpenCode Agents

This repository contains a small set of OpenCode agent definitions. The OpenCode core is isolated under `agents/`, leaving the repository root for project-level documentation and instructions.

## Agents

| Agent | Mode | File | Purpose |
|---|---|---|---|
| Bob the Builder | Primary | `agents/primary/Bob the Builder.md` | Implements approved plans and runs the quality pipeline. |
| Dora the Explorer | Primary | `agents/primary/Dora the Explorer.md` | Gathers requirements and creates implementation plans. |
| Butt Stallion | Subagent | `agents/subagent/Butt Stallion.md` | Generates unconventional ideas during planning. |
| Dexter | Subagent | `agents/subagent/Dexter.md` | Writes or updates tests for modified code. |
| Gatsby | Subagent | `agents/subagent/Gatsby.md` | Audits HTML-generating files for SEO issues. |
| Hancock | Subagent | `agents/subagent/Hancock.md` | Finds dead code and proposes safe cleanup. |
| Hermione | Subagent | `agents/subagent/Hermione.md` | Reviews code for correctness, performance, and maintainability. |
| Neo | Subagent | `agents/subagent/Neo.md` | Performs security audits and threat-focused reviews. |
| Oracle | Subagent | `agents/subagent/Oracle.md` | Researches current external documentation and advisories. |
| Otis | Subagent | `agents/subagent/Otis.md` | Writes and updates project documentation. |
| Samuel Morse | Subagent | `agents/subagent/Samuel Morse.md` | Probes real APIs with curl before integration work. |
| Timmy | Subagent | `agents/subagent/Timmy.md` | Audits HTML-generating files for accessibility issues. |
| Turing | Subagent | `agents/subagent/Turing.md` | Runs numerical calculations and data analysis via Python. |

## Notes

- Agent filenames intentionally include spaces because prompts reference names like `@Bob the Builder` and `@Samuel Morse`.
- Most agents have no internet access; `Oracle` is the dedicated web research agent.
- See `AGENTS.md` for repository-specific maintenance instructions.
