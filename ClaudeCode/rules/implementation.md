# Implementation pipeline

Implementation executes an approved plan. It does not re-plan. If the plan is
ambiguous, ask one clarifying question before starting — do not start implementing
a guess.

Check that a git repository is initialised before modifying anything.

Unless the user says otherwise, always work on a new branch, never directly on `main`.
Before modifying anything, switch to `main`, run `git pull` so it matches the remote,
and create the branch from there. If the working tree has uncommitted changes, ask
before switching rather than stashing or discarding them.

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
- **AI context** — `AGENTS.md`, `CLAUDE.md`, `docs/ai/**/*.md`, `.claude/rules/**`,
  `.claude/context/**`, `.claude/agents/**`, `.claude/skills/**`
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

Never call an agent without input. Before invoking a quality-gate agent, read
`~/.claude/context/pipeline-reports.md` for the exact input each agent expects.

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
4. **If the same finding persists after 2 fix attempts**, stop and report it with the
   `PIPELINE BLOCKED` block; read `~/.claude/context/pipeline-reports.md` for its format.

Never loop more than twice on the same problem.

## Loop detection

Track your own progress. Stop immediately and report if:

- You have modified the same file more than 3 times for the same reason
- An agent keeps returning the same finding after your fixes
- You are unsure whether your last change made things better or worse

Report the stop with the `LOOP DETECTED` block; read `~/.claude/context/pipeline-reports.md`
for its format.

Stopping cleanly is better than shipping broken code.

## Documentation ownership

`curator` is the sole owner of AI-facing documentation: the AI context paths listed under
change classification above, and agent-context Markdown. Do not edit those directly during
implementation. How that content is split between the root file, `docs/ai/`, and `docs/`
is defined in `~/.claude/agents/curator.md` (Context tiers).

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

1. Write the tracked pending set as the silent update timing section of
   `user-knowledge.md` defines: its denied-write, failed-write, and "Before the
   implementation final summary" bullets.
2. Report every change made during the whole conversation in the summary's
   `Knowledge profile:` line, in the format of the Transparency section of
   `user-knowledge.md`.

After a `PIPELINE BLOCKED` or `LOOP DETECTED` stop, that one-line report goes after the
block.

## Final summary

Before writing the final summary, read `~/.claude/context/pipeline-reports.md` and fill in
its final summary template: changes made, a pipeline results row per gate (with the reason
for every skipped gate), non-blocking findings, ready to ship, and the
`Knowledge profile:` line.

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
