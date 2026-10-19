# Workflow

Use Plan mode for planning and Auto or Manual mode for implementation.

After implementation, classify the changes and use specialized agents
when their expertise is relevant.

Do not invoke agents mechanically when they add no value.

# Project context

The project root file (`AGENTS.md` or `CLAUDE.md`) indexes `docs/ai/` (AI context) and
`docs/` (human docs). Before acting, read the files whose description matches the task.

# User knowledge profile

How well the user knows each technical domain, used to calibrate explanations (see
`rules/user-knowledge.md`):

@~/.claude/user-knowledge.md