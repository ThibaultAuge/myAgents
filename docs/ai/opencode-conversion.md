---
description: Use when porting, comparing, or referencing an OpenCode agent or orchestrator against its Claude Code counterpart.
---

# OpenCode to Claude Code conversion

## Current State
The status of `OpenCode/` is stated in the Scope section of `AGENTS.md`. Its `primary/` and `subagent/` layout is described in [README.md, Legacy: OpenCode](../../README.md#legacy-opencode), and the mapping of the OpenCode orchestrators to Claude Code rules in [README.md, Rules](../../README.md#rules).

Claude Code has no `primary` mode: every file in `agents/` is a subagent invoked from the main session, so orchestrators became rules, not agents.

## Relevant Files
- `OpenCode/agents/primary/`, `OpenCode/agents/subagent/`
- `ClaudeCode/agents/`, `ClaudeCode/rules/`

## Usage
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

## Notes
- `temperature:` needs attention when converting: `Butt Stallion` relied on `0.9` and `Turing` on `0.0`. Both now state that intent in prose, and that prose is the only thing holding the behavior.
- OpenCode filenames include spaces because OpenCode prompts reference names like `@Bob the Builder`. Claude Code filenames must not (see `docs/ai/agent-files.md`).
