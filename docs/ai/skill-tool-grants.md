---
description: Use when creating or editing a skill in `ClaudeCode/skills/`, especially its `allowed-tools` frontmatter.
---

# Skills and tool grants

## Current State
`ClaudeCode/skills/` holds one folder per skill with a `SKILL.md` inside:
- `jira-comment/` — Jira status comment drafted after the pipeline. It is the first file in this repo to use `Bash(verb:*)` prefix grants in frontmatter (every agent uses a plain `tools:` list), so it sets a precedent: understand the semantics below before copying that frontmatter.
- `knowledge/` — `/knowledge`; see `docs/ai/user-knowledge-profile.md`.

The **folder name** becomes the slash command (`/jira-comment`); the `name:` field is display only. The two must be identical and kebab-case for the command to read as documented.

## Relevant Files
- `ClaudeCode/skills/<name>/SKILL.md`
- `ClaudeCode/rules/implementation.md` (cites `jira-comment`), `ClaudeCode/rules/user-knowledge.md` (cites `knowledge`)

## Usage
- **No orphan skills.** A skill is user-invoked and never strictly unreachable, but a slash command nobody is told to type is dead weight. Every skill must be named at least once from `ClaudeCode/rules/`. `jira-comment` is cited by the post-pipeline step at the end of `implementation.md`; delete that reference and the skill has to go with it. `knowledge` is cited from `user-knowledge.md`.
- A `Bash(verb:*)` grant must name a verb that is read-only *as a verb* and cannot mutate state whatever flags trail it. The exact permitted command forms, and the flags forbidden despite matching the prefix, belong in the skill's own prose — `jira-comment` carries them in its Command Contract.
- Any change to a skill's `allowed-tools` requires a `neo` security audit. The documentation notes that "a skill can grant itself broad tool access, so review the `allowed-tools` of skills checked into a repository before you run Claude Code there", and the skills staged here are distributed to other developers' machines.

Verification checks for `ClaudeCode/skills/`: frontmatter parses; the containing folder name is kebab-case and equals `name:`; every `allowed-tools` entry names a real Claude Code tool, and every `Bash(...)` entry a real command prefix written as `Bash(verb:*)`; the skill is cited from `rules/`.

## Notes
Grant semantics, per the Claude Code documentation:
- **`allowed-tools` is a grant, not a restriction.** It "does not restrict which tools are available: every tool remains callable, and your permission settings still govern tools that are not listed." It pre-approves the listed tools for the turn that invokes the skill; the grant clears at the user's next message. **Removing a tool from `allowed-tools` removes no capability** — it only restores the normal permission prompt. Read a diff dropping `Read` as "this will now ask", never "this can no longer read files". A skill is confined only by its own prose, sandboxing, or a `PreToolUse` hook.
- **`Bash(prefix:*)` is not a raw string prefix match.** `:*` equals a trailing ` *` and the space is significant — `Bash(ls *)` does not match `lsof`. Matching happens after stripping a fixed wrapper set (`timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin`, `noglob`, bare `xargs`) and leading known-safe environment assignments.
- **Compound commands are split before matching**, on `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines; every subcommand must match a rule independently. `Bash(git diff:*)` does not approve `git diff HEAD && rm -rf x`.
- **Command substitution is unconfirmed.** Deny and ask rules are documented to descend into `$(...)` and backticks; allow rules are not documented either way. Assume neither, and never write a grant whose safety depends on the answer.
- **Precedence is deny, then ask, then allow.** First match wins and specificity does not matter, so an allow rule can never carve an exception out of a deny rule.
- **A prefix constrains the start of a command, not the flags that follow.** The documentation warns that patterns attempting to constrain arguments are fragile.
