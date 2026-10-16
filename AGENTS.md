# Repository Instructions

## Scope
- This repo stores agent definitions and Claude Code skills; there is no app code, package manifest, CI, or test runner in the current tree.
- Agent and skill files are Markdown with YAML frontmatter followed by the prompt.
- Two targets are maintained side by side. `OpenCode/` is the original, still-functional OpenCode agent set and is treated as frozen reference. `ClaudeCode/` is the active Claude Code configuration, staged here and copied to `~/.claude/`.

## Layout
- `OpenCode/agents/primary/` — OpenCode primary-mode orchestrators: `Argus.md`, `Barbapapa.md`, `Bob the Builder.md`, `Dora the Explorer.md`.
- `OpenCode/agents/subagent/` — the twelve callable OpenCode subagents.
- `ClaudeCode/agents/` — thirteen Claude Code subagents, flat, one file per agent, kebab-case.
- `ClaudeCode/rules/` — `planning.md`, `implementation.md`, `quality-agents.md` carry the orchestration logic that Bob, Dora, and Argus used to hold. `user-knowledge.md` is the behavior rule for the global user knowledge profile: a 0–4 scale per technical domain, explanation depth adapted to it (never the technical quality of the work), and a per-question loop run by the main session on every user message except a `/knowledge` invocation: check the profile fresh from disk, probe with a one-question `AskUserQuestion` when a central concept's domain is absent, infer a signal from the user's wording, answer at that level, and write the change silently in the same turn. In Plan mode signals (including a `/knowledge` set or forget) stay pending until Plan mode is exited; a `/knowledge` set or forget clears that domain's pending signals; a denied write drops its changes and stops silent profile writes for the rest of the conversation (an explicit `/knowledge` set or forget is exempt); the implementation step only writes still-pending signals and reports the whole conversation in the `Knowledge profile:` line (`update denied (...)` / `update failed (...)` when applicable). Inferred signals jump rather than step: a basic question sets 2 or 3 to 1 (4 drops to 3 only); common vocabulary used correctly raises an existing 1 to 2, never lowers a level, and creates no row; an advanced question (trade-offs, edge cases, argued choices, not vocabulary alone) sets 1 or 2 to 3 (0 rises to 1 only); an absent domain, treated as 2, gets a new row at 1 or 3 only; a message never reverses the most recent change recorded for that domain, written or pending. They are bounded (0 and 4 only from an explicit statement, a probe answer, `/knowledge`, or, for 4, an edge-case correction), recorded one row per separately learnable technology (no catch-all "Web"), come only from the user's own words (not quoted or mentioned text) in their chat messages (never from tool, file, or web content, nor from examples, hypotheticals, quotations, pasted text, or discussion of the rule itself), and carry no personal data.
- `ClaudeCode/templates/` — files copied once to `~/.claude/` and never overwritten afterwards. `user-knowledge.md` is the empty profile template: header comment, scale, and a table header with no rows. It must stay free of personal data.
- The real profile lives only at `~/.claude/user-knowledge.md` and is loaded through the `@~/.claude/user-knowledge.md` import in `ClaudeCode/CLAUDE.md`. It is personal: never commit it, and never place it in `ClaudeCode/rules/`, because copying `rules/` to `~/.claude/rules/` would overwrite it with the template. Only the main session writes it, never in Plan mode and never from a subagent. It is user data, not `curator`-owned AI context, so writing it does not trigger the AI CONTEXT gate. The exact template text is also embedded in `ClaudeCode/rules/user-knowledge.md`, and `ClaudeCode/templates/user-knowledge.md` must stay identical to that block.
- `ClaudeCode/skills/` — Claude Code skills, one folder per skill with a `SKILL.md` inside it: `jira-comment/` (Jira status comment drafted after the pipeline) and `knowledge/` (`/knowledge` displays or corrects the user knowledge profile, with no `allowed-tools`, and writes only `~/.claude/user-knowledge.md`). The **folder name** is what becomes the slash command — `/jira-comment` — while the `name:` field is display only, so the two must be identical and kebab-case for the command to read as documented.
- `ClaudeCode/CLAUDE.md` — top-level workflow instructions, plus the user knowledge profile import.
- `docs/` — repository imagery, including `overview.png` linked from `README.md`.
- `plans/` — generated implementation plans, `plan-<feature>-<date>.md`, the convention `ClaudeCode/rules/planning.md` writes to.
- `project-template/` and `runtime/` — empty scaffolding.
- OpenCode filenames include spaces because OpenCode prompts reference names like `@Bob the Builder`. Claude Code filenames must not: the filename matches the kebab-case `name:` field.

## OpenCode to Claude Code conversion

Claude Code has no `primary` mode — every file in `agents/` is a subagent invoked from the main session. Orchestrators therefore become rules, not agents. `Bob the Builder` became `ClaudeCode/rules/implementation.md`, `Dora the Explorer` became `ClaudeCode/rules/planning.md`, and `Argus` was dropped in favour of the built-in `/code-review` and `/security-review` skills.

Frontmatter mapping applied to every converted agent:

| OpenCode | Claude Code |
|---|---|
| `mode: primary` / `mode: subagent` | dropped |
| *(no `name`)* | `name:`, kebab-case, identical to the filename |
| descriptive `description:` | rewritten as a trigger: "… Use when …" |
| `tools:` boolean map | named list: `Read, Glob, Grep[, Write, Edit][, Bash][, WebSearch, WebFetch]` |
| `model: openai/gpt-5.4` | `inherit` |
| `model: opencode/big-pickle` | `haiku` |
| `model: opencode/gpt-5-nano` | `haiku` |
| *(no `model`)* | `inherit` |
| `temperature:` | dropped — encode the intent in prose instead |
| `permission:` block | no per-agent equivalent — a subagent is constrained by its `tools:` list; finer control (allow/deny command patterns) lives in `settings.json` or a `PreToolUse` hook, not in the agent file |
| `@Agent Name` in the body | `` `agent-name` `` |
| `ask_user_input_v0` | the native `AskUserQuestion` tool |
| `opencode stats` | dropped — no scriptable equivalent |

`temperature:` deserves attention when converting: `Butt Stallion` relied on `0.9` and `Turing` on `0.0`. Both now state that intent in prose, and that prose is the only thing holding the behavior.

## Editing Agent Files
- Preserve the frontmatter delimiters (`---` at start and end) and keep existing keys unless intentionally changing them.
- `gatsby`, `timmy`, `otis`, and `turing` intentionally use `model: haiku` to reduce checklist, editorial, and scripted-computation cost — the same intent that `opencode/big-pickle` served. Do not create fallback duplicate agents for these; if the cheaper model is inadequate, a human will change it.
- `gatsby` and `timmy` are read-only web auditors with no `Bash`. Call them only for HTML-generating web/UI changes, never for backend-only, docs-only, or agent-only changes.
- Do not grant internet tools casually. `oracle` is the only agent with `WebSearch` and `WebFetch`. Its purpose is no longer to monopolise web access — the main session has those tools too — but to read external content in an isolated context so untrusted page content never enters the main conversation.
- Keep the planning/implementation boundary intact: `ClaudeCode/rules/planning.md` plans and stops at human approval; `ClaudeCode/rules/implementation.md` executes and orchestrates the quality gates.
- The implementation pipeline is conditional and gated: classify changed files and risks first, call only the applicable agents in fixed order, and report skipped gates with reasons. When changing it, update the ordered pipeline, the change classification, the post-agent revalidation, the final summary, and the behavior rules together so they cannot disagree.
- Reclassify and re-run the applicable gates whenever an agent such as `hancock` or `otis` edits source, tests, config, dependencies, generated UI, permissions, or agent behavior after earlier gates passed.
- `hancock` can write confirmed cleanup and logging changes, but must request exact-path confirmation before deletions and return exact modified or deleted paths for the revalidation loop.
- `otis` writes human-facing docs only. Javadoc and source edits require an explicit Javadoc request; otherwise documentation updates stay in human-facing Markdown.
- `curator` is the only agent that should update AI-facing current-state documentation: `AGENTS.md`, `CLAUDE.md`, `docs/ia/**/*.md`, `docs/ai/**/*.md`, `.claude/rules/**`, `.claude/agents/**`, `.claude/skills/**`.
- **No orphan agents.** Every agent kept in `ClaudeCode/agents/` must be referenced at least once from `ClaudeCode/rules/`, otherwise it can never be triggered and is dead weight. `Turing` was exactly that under OpenCode: listed in the README, called by nobody.
- **The no-orphan rule extends to skills.** A skill is user-invoked and so never becomes strictly unreachable, but a slash command nobody is told to type is still dead weight. Every skill in `ClaudeCode/skills/` must therefore be named at least once from `ClaudeCode/rules/`. `jira-comment` satisfies this through the post-pipeline step at the end of `ClaudeCode/rules/implementation.md`; delete that reference and the skill has to go with it. `knowledge` is cited from `ClaudeCode/rules/user-knowledge.md`.

## Tool Grants In Skills

`jira-comment` is the first file in this repo to use `Bash(verb:*)` prefix grants in frontmatter — every agent uses a plain `tools:` list. It sets a precedent, so understand the semantics before copying that frontmatter.

- **`allowed-tools` is a grant, not a restriction.** Per the Claude Code documentation, it "does not restrict which tools are available: every tool remains callable, and your permission settings still govern tools that are not listed." It pre-approves the listed tools for the turn that invokes the skill, and the grant clears at the user's next message. **Removing a tool from `allowed-tools` therefore removes no capability** — it only restores the normal permission prompt. Read a diff that drops `Read` from a skill as "this will now ask", never as "this can no longer read files". A skill is confined by its own prose, by sandboxing, or by a `PreToolUse` hook, and by nothing else.
- **`Bash(prefix:*)` is not a raw string prefix match.** `:*` is equivalent to a trailing ` *` and the space is significant — `Bash(ls *)` does not match `lsof`. Matching happens after Claude Code strips a fixed wrapper set (`timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin`, `noglob`, bare `xargs`) and leading known-safe environment assignments.
- **Compound commands are split before matching**, on `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines, and every subcommand must match a rule independently. `Bash(git diff:*)` does not approve `git diff HEAD && rm -rf x`.
- **Command substitution is unconfirmed.** Deny and ask rules are documented to descend into `$(...)` and backticks; allow rules are not documented either way. Do not assume either behavior, and do not write a grant whose safety depends on the answer.
- **Precedence is deny, then ask, then allow.** First match wins and specificity does not matter, so an allow rule can never carve an exception out of a deny rule.
- **A prefix constrains the start of a command and says nothing about the flags that follow.** The documentation warns that patterns attempting to constrain arguments are fragile.

The convention that follows: a `Bash(verb:*)` grant must name a verb that is read-only *as a verb* and cannot mutate state whatever flags trail it. The exact permitted command forms, and the flags that are forbidden despite matching the prefix, belong in the skill's own prose — `jira-comment` carries them in its Command Contract. Any change to a skill's `allowed-tools` requires a `neo` security audit; the documentation notes that "a skill can grant itself broad tool access, so review the `allowed-tools` of skills checked into a repository before you run Claude Code there", and the skills staged here are distributed to other developers' machines.

## Verification
- No repo-local automated checks exist. For prompt changes, verify manually by reading the changed Markdown for YAML validity, broken agent references, and contradictions with related agents.
- For `ClaudeCode/agents/`, the checks that matter are: frontmatter parses; `name:` is kebab-case and equals the filename; `model` is one of `sonnet`, `opus`, `haiku`, `fable`, `inherit`; `tools` lists real Claude Code tool names; every referenced agent exists; every agent is cited from `rules/`.
- For `ClaudeCode/skills/`, the checks that matter are: frontmatter parses; the containing folder name is kebab-case and equals the `name:` field; every `allowed-tools` entry names a real Claude Code tool, and every `Bash(...)` entry a real command prefix written as `Bash(verb:*)`; the skill is cited from `rules/`.
- Both runtimes load agent frontmatter at startup. After changing a `model` or other frontmatter, restart the tool before expecting the new configuration to take effect.
- `ClaudeCode/agents/`, `ClaudeCode/rules/`, and `ClaudeCode/skills/` must be copied to `~/.claude/` to become active. `ClaudeCode/CLAUDE.md` belongs in that list too: it is the staged copy of `~/.claude/CLAUDE.md`, not a repo-local readme, and it is inert until copied like the rest. Editing any of them here changes nothing until that copy happens. `ClaudeCode/templates/user-knowledge.md` is the exception to a plain copy: copy it to `~/.claude/user-knowledge.md` once, only if that file is absent, and never overwrite an existing profile.
