---
description: Use when invoking a quality-gate agent, a lot subagent, or the grumpy plan critic, reporting a blocked pipeline or loop, or writing the implementation final summary.
---

# Pipeline inputs and reports

On-demand companion to `~/.claude/rules/implementation.md`. The rule decides which gates
run, in which wave, and when to stop; this file holds what to pass each agent and the
exact report formats.

## What to pass each agent

- **lot subagent (`general-purpose`)** — the plan file path and the lot's Work Breakdown
  row and spec, plus the plan's Edge Cases, Security Constraints, and Compliance
  Constraints entries relevant to
  the lot; the contract file paths; the exclusive list of the lot's files (AI-context
  files may be on it) and the files it must not touch; the acceptance command, scoped to
  the lot's files for a same-checkout lot; a pointer to the project root context file
  (`AGENTS.md` or `CLAUDE.md`). State explicitly that it is a lot subagent bound by the
  lot subagent guard in `implementation.md` (Contract and lots). For a worktree lot, add: first check
  that the contract files are present and, if not, stop and report; commit the work on
  the branch the harness created. Expected return: files changed, deviations from the
  contract, open questions, and the branch name for a worktree lot.

- **`dexter`** — the modified files and a summary of what changed
- **`hermione`** — the modified files only, not the full codebase
- **`gatsby`** — only files that generate HTML output (templates, components, pages,
  metadata)
- **`timmy`** — only files that generate HTML output or UI behavior (templates,
  components, pages, forms)
- **`neo`** — the modified files plus the specific security-sensitive changes: auth,
  secrets, permissions, external calls, user input, config, dependencies, env vars,
  tool permissions, model/provider routing
- **`phoenix-wright`** — the modified files, a summary of the personal-data changes
  (fields, purposes, retention, third parties, cookies or trackers), the paths of the
  project's legal documents if known, the project's `Jurisdiction:` line from `~/.claude/agent-opt-outs.md` if any (never from another source), and the
  plan's Compliance Constraints if the plan has them. In planning, the feature
  description and data flows instead of modified files
- **`grumpy`** (planning, Phase 4) — the plan file path, the project root, and the path of
  its root context file (`AGENTS.md` or `CLAUDE.md`). Nothing else: not the
  conversation, not a summary of it, not your opinion of the plan or of the
  alternatives, so its critique stays independent of the reasoning that produced the plan
- **`hancock`** — the list of files modified during this implementation and a summary
  of components or functions added or replaced
- **`curator`** — the modified files, a summary of behavior changes, any reuse
  guidance future agents must know, and the root context file size before and after the
  change, measured by the main session (`wc -c`)
- **`otis`** — a summary of what changed and which human-facing doc types are
  affected (README / API reference / user guide)

## PIPELINE BLOCKED report

Used when the same blocking finding persists after 2 fix attempts.

```
🚫 PIPELINE BLOCKED
Step: [step name]
Finding: [exact finding from the agent]
Attempts: 2
Status: Unable to resolve — human intervention required.
```

## LOOP DETECTED report

Used when a loop-detection condition in the rule is met.

```
⚠️ LOOP DETECTED
I have attempted to resolve [issue] [N] times without progress.
Last state: [what was tried]
Recommended next step: [honest assessment of what a human should do]
```

## Final summary template

---
### Implementation Summary

**Changes made**
Brief description of what was implemented.

**Work split:** [contract — main session; lot A — subagent; lot B — main session | none]

**Pipeline results**

| Step | Status | Notes |
|---|---|---|
| Tests | ✅ / ⏭ / ⚠️ / 🚫 | |
| Review | ✅ / ⏭ / ⚠️ / 🚫 | |
| SEO | ✅ / ⏭ / ⚠️ / 🚫 | (⏭ = skipped, no web files, or opted out by user: reason (key)) |
| Accessibility | ✅ / ⏭ / ⚠️ / 🚫 | (⏭ = skipped, no web files, or opted out by user: reason (key)) |
| Security | ✅ / ⏭ / ⚠️ / 🚫 | |
| Legal | ✅ / ⏭ / ⚠️ / 🚫 | (⏭ = skipped, no personal data, or opted out by user: reason (key)) |
| Cleanup | ✅ / ⏭ / ⚠️ / 🚫 | |
| AI Context | ✅ / ⏭ / ⚠️ / 🚫 | |
| Documentation | ✅ / ⏭ / ⚠️ / 🚫 | |

**Non-blocking findings to address later**
The 🟡 and 🔵 findings from review, security, and legal that were not fixed in this pass,
any conflict between two Wave 2 audits with the severity that was followed, and any
opt-out naming an agent that cannot be opted out.

**Waived findings:** [each `phoenix-wright` 🔴 the user waived in chat, with their words | none]

**Ready to ship:** YES / NO

Knowledge profile: [PHP 3→4, OpenTelemetry metrics 0→1 | unchanged | update denied (PHP 3→4 not written) | update failed (PHP 3→4 not written)]

---
