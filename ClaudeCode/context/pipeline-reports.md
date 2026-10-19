---
description: Use when invoking a quality-gate agent, reporting a blocked pipeline or loop, or writing the implementation final summary.
---

# Pipeline inputs and reports

On-demand companion to `~/.claude/rules/implementation.md`. The rule decides which gates
run, in what order, and when to stop; this file holds what to pass each agent and the
exact report formats.

## What to pass each agent

- **`dexter`** — the modified files and a summary of what changed
- **`hermione`** — the modified files only, not the full codebase
- **`gatsby`** — only files that generate HTML output (templates, components, pages,
  metadata)
- **`timmy`** — only files that generate HTML output or UI behavior (templates,
  components, pages, forms)
- **`neo`** — the modified files plus the specific security-sensitive changes: auth,
  secrets, permissions, external calls, user input, config, dependencies, env vars,
  tool permissions, model/provider routing
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

**Pipeline results**

| Step | Status | Notes |
|---|---|---|
| Tests | ✅ / ⏭ / ⚠️ / 🚫 | |
| Review | ✅ / ⏭ / ⚠️ / 🚫 | |
| SEO | ✅ / ⏭ / ⚠️ / 🚫 | (⏭ = skipped, no web files) |
| Accessibility | ✅ / ⏭ / ⚠️ / 🚫 | (⏭ = skipped, no web files) |
| Security | ✅ / ⏭ / ⚠️ / 🚫 | |
| Cleanup | ✅ / ⏭ / ⚠️ / 🚫 | |
| AI Context | ✅ / ⏭ / ⚠️ / 🚫 | |
| Documentation | ✅ / ⏭ / ⚠️ / 🚫 | |

**Non-blocking findings to address later**
The 🟡 and 🔵 findings from review and security that were not fixed in this pass.

**Ready to ship:** YES / NO

Knowledge profile: [PHP 3→4, OpenTelemetry metrics 0→1 | unchanged | update denied (PHP 3→4 not written) | update failed (PHP 3→4 not written)]

---
