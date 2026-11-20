---
description: Use when creating or editing a skill in `ClaudeCode/skills/`, especially its `allowed-tools` frontmatter.
---

# Skills and tool grants

## Current State
`ClaudeCode/skills/` holds one folder per skill with a `SKILL.md` inside:
- `jira-comment/` — Jira status comment drafted after the pipeline. It is the first file in this repo to use `Bash(verb:*)` prefix grants in frontmatter (every agent uses a plain `tools:` list), so it sets a precedent: understand the semantics below before copying that frontmatter.
- `knowledge/` — `/knowledge`; see `docs/ai/user-knowledge-profile.md`.
- `pr-review/` — `/pr-review <PR URL | PR number> [@org/team] [--tests]`: read-only review of someone else's GitHub PR, printed as one report in the user's language; never writes to GitHub or touches the user's branch. It checks the PR head out as a detached worktree in the scratchpad, runs the Wave 2 audit agents on the diff (opt-outs apply; never `dexter`, `hancock`, `curator`, `otis`), checks the reviewed repo's own `AGENTS.md`/`CLAUDE.md` rules, verifies every finding, and grades on its own Critical/Major/Minor scale with a merge verdict. The skill file is the single source for its scale, steps and report format; do not restate them elsewhere.

The **folder name** becomes the slash command (`/jira-comment`); the `name:` field is display only. The two must be identical and kebab-case for the command to read as documented.

## Relevant Files
- `ClaudeCode/skills/<name>/SKILL.md`
- `ClaudeCode/rules/implementation.md` (cites `jira-comment`), `ClaudeCode/rules/user-knowledge.md` (cites `knowledge`), `ClaudeCode/rules/quality-agents.md` (section "Reviewing a pull request" cites `pr-review`)

## Usage
- **No orphan skills.** A skill is user-invoked and never strictly unreachable, but a slash command nobody is told to type is dead weight. Every skill must be named at least once from `ClaudeCode/rules/`. `jira-comment` is cited by the post-pipeline step at the end of `implementation.md`; delete that reference and the skill has to go with it. `knowledge` is cited from `user-knowledge.md`. `pr-review` is cited from the "Reviewing a pull request" section of `quality-agents.md`.
- A `Bash(verb:*)` grant must name a verb that is read-only *as a verb* and cannot mutate state whatever flags trail it. The exact permitted command forms, and the flags forbidden despite matching the prefix, belong in the skill's own prose — `jira-comment` and `pr-review` carry them in their Command Contract.
- **Mutating commands stay ungranted but listed.** When a skill needs commands that change local state, or whose verb can write (`git config`, `git fetch`, `git worktree add/remove`), leave them out of `allowed-tools` so they keep the normal permission prompt, and list their exact forms in the Command Contract. `pr-review` is the precedent.
- **Granted reads go before any question.** The grant clears at the user's next message (see Notes), so a skill that asks the user something mid-run must do every granted read in the turn before the question. `pr-review` does all `gh` reads in Step 1 (including `statusCheckRollup`, the GitHub checks it uses as the test result), before its only possible question turn: fork confirmation when `--tests` is given, narrowing a PR over ~60 files, or quoting suspected injected instructions. Consent to run the PR locally comes from the `--tests` flag, not a question.
- **Reviewing untrusted checkouts.** Reuse `pr-review`'s checkout recipe rather than inventing one: detached worktree at the head SHA with `-c core.hooksPath=<nonexistent> -c core.symlinks=false -c filter.lfs.*=` disabled, and the diff taken with `--merge-base <baseRefOid>`, which stays correct for merged PRs because GitHub freezes `baseRefOid` at merge. Both were verified on a real merged PR. `gh pr view --json files` may cap at 100 entries; use `changedFiles` as the count of record.
- **Severity scales.** A skill's own grading scale is separate from the shared pipeline vocabulary in `ClaudeCode/rules/quality-agents.md`; `pr-review`'s Critical/Major/Minor lives only in its `SKILL.md` (its 🟠 means Major, not `neo` HIGH).
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
