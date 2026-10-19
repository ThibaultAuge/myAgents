# Workflow

Use Plan mode for planning and Auto or Manual mode for implementation.

After implementation, classify the changes and use specialized agents
when their expertise is relevant.

Do not invoke agents mechanically when they add no value.

# Project context

The project root file (`AGENTS.md` or `CLAUDE.md`) indexes `docs/ai/` (AI context) and
`docs/` (human docs). Before acting, read the files whose description matches the task.

If a file a rule points to under `~/.claude/context/` is missing, stop a planning or pipeline
step and tell the user to install `context/`. For a probe or profile creation, skip the probe,
answer at level 2, keep the change pending, and mention the missing install once. Never
improvise its content, least of all the profile template.

# User knowledge profile

How well the user knows each technical domain, used to calibrate explanations (see
`rules/user-knowledge.md`):

@~/.claude/user-knowledge.md