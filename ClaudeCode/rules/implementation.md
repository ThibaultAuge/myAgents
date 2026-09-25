# Implementation pipeline

Implementation executes an approved plan. It does not re-plan. If the plan is
ambiguous, ask one clarifying question before starting — do not start implementing
a guess.

Check that a git repository is initialised before modifying anything.

## Change classification

Before running any quality gate, classify what actually changed:

- **Code/behavior** — source code, public APIs, build scripts, runtime behavior
- **Tests** — test files, fixtures, test configuration
- **Web UI** — HTML, JSX, TSX, Vue, Svelte, Astro, templates, pages, metadata,
  forms, interactive components
- **Security-sensitive** — auth, secrets, permissions, external calls, user input,
  config, dependencies, environment variables, tool permissions — including a skill's
  `allowed-tools` — model/provider routing
- **Dependencies/config** — manifests, lockfiles, CI config, build and runtime config
- **Docs** — README, API reference, guides, changelog, Javadoc
- **AI context** — `AGENTS.md`, `CLAUDE.md`, `docs/ia/**/*.md`, `docs/ai/**/*.md`,
  `.claude/rules/**`, `.claude/agents/**`, `.claude/skills/**`
- **Cleanup/refactor** — removals, renames, replacements, large refactors

When unsure, choose the safer relevant checks and explain why.

## Pipeline order

Run only the applicable gates, in this order. The order is fixed: each selected gate
assumes the previous selected gate came back clean.

```
1. TEST           → dexter        when code, tests, APIs, build scripts, or a
                                  non-trivial agent workflow changed
2. REVIEW         → hermione      when code or a complex prompt/workflow changed
3. SEO            → gatsby        HTML-generating web files only
4. ACCESSIBILITY  → timmy         HTML-generating web/UI files only
5. SECURITY       → neo           auth, secrets, permissions, external calls, user
                                  input, config, dependencies, env vars, tool
                                  permissions, model/provider changes
6. CLEANUP        → hancock       refactors, removals, renames, large changes, or
                                  replaced components/functions
7. AI CONTEXT     → curator       when durable AI-facing context changed
8. DOCUMENT       → otis          when README, API reference, user guide, changelog,
                                  or Javadoc is affected
```

Do not run selected gates in parallel. If a gate produces a blocking finding, stop
there. Record the reason for every skipped gate in the final summary.

Two gates need you to do part of the work yourself, because the agent cannot:

- **`dexter` writes tests but has no `Bash`.** It cannot run them. After it returns, you
  run the suite and you own the pass/fail verdict for the TEST gate. A gate marked ✅
  without an executed suite is a false report.
- **`hancock` cannot reach the user.** It returns a dead-code report plus a confirmation
  request and stops. Relay that report, obtain an explicit yes, then invoke `hancock`
  again with the confirmed paths. Never treat its own report as the confirmation.

See `quality-agents.md` for the full signal-to-agent routing table.

**Web gating.** Do not call `gatsby` or `timmy` unless the modified files include
HTML, JSX, TSX, Vue, Svelte, Astro, templates, page metadata, routes/pages, or other
rendered public UI or content. Backend-only changes never trigger them.

## What to pass each agent

Never call an agent without input.

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
- **`curator`** — the modified files, a summary of behavior changes, and any reuse
  guidance future agents must know
- **`otis`** — a summary of what changed and which human-facing doc types are
  affected (README / API reference / user guide)

## Post-agent edit revalidation

If `hancock`, `otis`, or any other agent edits source, tests, config, dependencies,
generated UI, permissions, or agent behavior after earlier gates passed:

1. Treat those edits as a new implementation delta.
2. Reclassify the changed files.
3. Re-run the applicable gates from the earliest affected one — usually `dexter`,
   then `hermione`, then the web audits if UI changed, then `neo` if security-sensitive.
4. Produce the final summary only after the post-agent edits have been validated.

If the agent only updated human-facing Markdown or reported findings without editing,
no revalidation is needed.

## Blocking behavior

If `hermione`, `gatsby`, or `timmy` returns a 🔴 BLOCKING finding, or `neo` returns a
🔴 CRITICAL finding:

1. **Stop the pipeline immediately** — do not proceed to the next gate.
2. **Fix the issue** if it is clearly scoped and contained.
3. **Re-run the failed gate** to confirm the fix resolves the finding.
4. **If the same finding persists after 2 fix attempts**, stop and report:

```
🚫 PIPELINE BLOCKED
Step: [step name]
Finding: [exact finding from the agent]
Attempts: 2
Status: Unable to resolve — human intervention required.
```

Never loop more than twice on the same problem.

## Loop detection

Track your own progress. Stop immediately and report if:

- You have modified the same file more than 3 times for the same reason
- An agent keeps returning the same finding after your fixes
- You are unsure whether your last change made things better or worse

```
⚠️ LOOP DETECTED
I have attempted to resolve [issue] [N] times without progress.
Last state: [what was tried]
Recommended next step: [honest assessment of what a human should do]
```

Stopping cleanly is better than shipping broken code.

## Documentation ownership

`curator` is the sole owner of AI-facing documentation: `AGENTS.md`, `CLAUDE.md`,
`docs/ia/**/*.md`, `docs/ai/**/*.md`, `.claude/rules/**`, `.claude/agents/**`,
`.claude/skills/**`, and agent-context Markdown. Do not edit those directly during
implementation.

`otis` owns human-facing documentation only: README files, API references, user
guides, tutorials, changelogs, and Javadoc. Never ask `otis` to update AI context docs.

`CLEANUP_LOG.md` is the one exception to that split: it is an operational record of what
`hancock` deleted, written by `hancock` itself for rollback purposes, not a changelog.

`~/.claude/user-knowledge.md` is another exception. The main session writes it under
`user-knowledge.md`. It is user data, not AI context owned by `curator`, and writing it
does not trigger the AI CONTEXT gate.

## Knowledge profile update

The profile is written as the conversation goes, one user message at a time, following
the per-question loop in `user-knowledge.md`. This step only closes it out, before the
final summary, silently and without asking for confirmation. It does not wait for the pull
request to be ready.

1. Write the tracked pending set, applied in order, after reading
   `~/.claude/user-knowledge.md` fresh from disk. Never re-derive it by rescanning the
   conversation. A change the user denied was dropped and is not retried.
2. Report every change made during the whole conversation in the summary's
   `Knowledge profile:` line, including denied ones as `update denied (...)`. If the
   pending record was lost to context compaction, report the changes still known in
   context.

A `PIPELINE BLOCKED` or `LOOP DETECTED` stop still runs this step, and the same one-line
report goes after that block.

## Final summary

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

Knowledge profile: [PHP 3→4, OpenTelemetry metrics 0→1 | unchanged | update denied (PHP 3→4 not written)]

---

## After the summary

Once the summary is out and the pull request is ready, offer the `jira-comment` skill:
`/jira-comment [TICKET-KEY]` drafts the short English status comment for the ticket and
prints it for the human to paste. It runs inline on purpose — the session's memory of
the questions asked and the difficulties actually met is the half of the comment no
diff can reconstruct. It never contacts Jira.

## Behavior rules

1. **Execute, do not re-plan** — ask one clarifying question if the plan is ambiguous,
   then implement what was approved.
2. **One change at a time** — implement and validate independent changes sequentially.
3. **Never skip security-sensitive changes** — anything touching auth, secrets,
   permissions, external API calls, user input handling, config, dependencies,
   environment variables, tool permissions, or model/provider routing always triggers
   `neo`, even for a minor edit.
4. **Web audits are gated** — `gatsby` and `timmy` only when rendered content changed.
5. **Preserve existing behavior** — unless the plan says otherwise, existing tests
   must still pass.
6. **Delegate AI docs** — call `curator` rather than editing AI-facing context yourself.
7. **Compute, do not infer** — every numeric or statistical result goes through the
   `turing` agent, which executes Python. Never produce arithmetic, statistics, or
   unit conversions from model inference, however trivial they look.
