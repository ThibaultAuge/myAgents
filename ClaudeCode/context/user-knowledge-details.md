---
description: Use when running a knowledge probe or creating a missing profile.
---

# User knowledge profile details

On-demand companion to `~/.claude/rules/user-knowledge.md`. The rule runs on every message
and decides when to probe, how signals move levels, and when to write; this file holds the
probe mechanics and the profile template.

## Probe details

- **Form**: `AskUserQuestion` with a single question and three options: `No notion` → 0,
  `Notions` → 1, `Everyday use` → 3.
- **Free answer**: if the user answers through "Other" and the answer clearly states a
  level, treat it as an explicit statement. If it does not, make no update and answer at
  level 2.
- **Ignored or off-topic answer**: make no update and answer at level 2.
- **Weight**: a probe answer counts as an explicit statement. Its Evidence reads
  `Probe answer: <option>`, for example `Probe answer: Notions`. For a free answer, write
  `Probe answer: Other (stated level N)` and never copy the user's text into Evidence.

## Template

Create a missing profile from exactly this text. `ClaudeCode/templates/user-knowledge.md`
must match it character for character, so if you change one, change the other.

```markdown
<!--
User knowledge profile. Copy this file to ~/.claude/user-knowledge.md once, and only if that
file does not already exist. The real profile is personal: never commit it.
Claude maintains it following ~/.claude/rules/user-knowledge.md. Correct it with /knowledge.
Record technical skills only, never personal information.
-->

# User knowledge profile

Scale: 0 unknown · 1 notions · 2 guided · 3 autonomous · 4 expert.
Domains that are not listed are treated as level 2.

| Domain | Level | Evidence | Updated |
|---|---|---|---|
```
