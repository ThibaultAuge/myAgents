---
description: Use when asking planning questions, writing a plan file, or deciding which plan lots can be delegated.
---

# Plan template and planning reference

On-demand companion to `~/.claude/rules/planning.md`. The rule decides when to ask, when
to stop, and where to save the plan; this file holds the reference material.

## Question banks by domain

**Business objective** — primary user type; success metric (what does "done" look
like?); must-have versus nice-to-have.

**Technical constraints** — existing stack (framework, database, hosting);
performance targets (response time, concurrent users, data volume); integration
requirements; deployment constraints (cloud provider, CI/CD, environments).

**UX/UI preferences** — design style (minimal, rich, brand-specific); interaction
patterns (modal, inline, wizard, drag-drop); accessibility requirements (WCAG level,
screen reader support); device support (desktop-only, mobile-first, responsive).

**Data and compliance** — which personal data is collected, and why each field is
needed; audience (public, internal, personal use only); jurisdiction; third parties
receiving the data; legal documents shown to users (terms of use, privacy policy,
legal notices).

## Plan template

Write the plan file from this template.

```markdown
# Implementation Plan — [Feature Name]

*Generated on [date]*

## Business Objective

[What this achieves for the business or its users]

## Requirements Summary

### Functional Requirements
- [Requirement]

### Non-Functional Requirements
- **Performance:** [expected behavior, constraints]
- **Security:** [auth, data handling, compliance]
- **UX/UI:** [design preferences, accessibility]

### Out of Scope
- [Explicitly what NOT to build]

## Technical Approach

### Architecture
[Components, data flow, integrations]

### Stack & Tools
- **Frontend:** [framework, libraries]
- **Backend:** [language, framework, database]
- **External APIs:** [list with authentication method]

### Files to Create/Modify
1. `path/to/file.ext` — [purpose]

## Work Breakdown

*(Always present. A plan with no separable parts writes "Single lot — main session" here and nothing else)*

### Contract (main session, first)
- [frozen interface: shared types, OpenAPI spec, DTOs, entity mapping]
- **Contract commit:** [yes — a lot uses `isolation: "worktree"` / no — all lots share the checkout]

### Lots

| Lot | Files (exclusive) | Depends on | Delegable | Acceptance check |
|---|---|---|---|---|
| [A] | [`path/…`] | [contract — the only allowed value for a delegable lot / lot X] | [yes, same checkout / yes, worktree / no — reason] | [test or command, scoped to the lot's files] |

## Creative Alternatives Considered

*(Only if `butt-stallion` was consulted)*

[1-3 ideas explored, with brief notes on why the chosen approach won]

## Security Constraints

*(Only if `neo` was consulted)*

- [Security rule]

If `neo` flagged CRITICAL or HIGH findings, they are addressed in the approach above.

## Compliance Constraints

*(Only if `phoenix-wright` was consulted)*

- [Compliance rule: purpose, minimisation, legal basis, retention, consent]
- **Legal documents to update:** [document — what it must now say | none]

If `phoenix-wright` flagged BLOCKING issues, they are addressed in the approach above.

## Performance Considerations

- **Expected bottlenecks:** [where performance could degrade]
- **Scale target:** [concurrent users, data volume, response time]
- **Optimizations planned:** [caching, indexing, pagination]

## API Integration Details

*(Only if `samuel-morse` was consulted — paste its Integration Reference block here)*

## Edge Cases & Error Handling

- [Edge case and how to handle it]

## Complexity Estimate

**Size:** XS / S / M / L / XL

**Justification:** [one sentence]
```

## Complexity estimation guide

- **XS** — single file, under 50 lines, no external dependencies, under 1 hour
- **S** — 1-3 files, simple logic, minimal integration, under 4 hours
- **M** — multiple components, moderate logic, 1-2 integrations, 1-2 days
- **L** — cross-cutting changes, complex logic, multiple integrations, 3-5 days
- **XL** — architectural change, new systems, high uncertainty, over a week

When in doubt, estimate higher.

## Delegation guide

Fills the plan's Work Breakdown. `implementation.md` delegates only the lots marked
Delegable there. A lot is delegable only if all four hold:

1. Its sole dependency is the contract. A lot that depends on another lot is
   implemented by the main session after that lot is integrated.
2. The lot shares no file with another lot.
3. It is verifiable on its own: its tests or a command. For a same-checkout lot, scope
   that command to the lot's own files where the toolchain allows, since other lots are
   editing the same tree.
4. It is large enough to beat the cost of the brief plus integration.

Mark a lot "yes, worktree" only when it runs commands with shared state (migrations
against a local database, code generation); then set Contract commit to yes. Approving
the plan then authorises the contract commit, each worktree lot's commit on its harness
branch, and the merges of those branches into the feature branch. Otherwise lots share the checkout and the
contract is not committed before they run.

Patterns:

- **API** — contract = the spec or the shared types; one lot for the provider, one lot
  for the consumer.
- **Database schema change** (e.g. Doctrine) — contract = the target schema (entity
  fields and types). Lot A = entities + migration; generating and applying the migration
  stays inside lot A because it depends on the mapping, and makes lot A a worktree lot.
  Lot B = repositories, queries, and services consuming the entities.

Anti-patterns, kept with the main session:

- A small, tightly coupled change.
- Shared hotspot files: i18n catalogs, route registration, DI/service config.
- Dependency installs and manifest or lockfile edits.
