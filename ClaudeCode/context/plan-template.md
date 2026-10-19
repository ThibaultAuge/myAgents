---
description: Use when asking planning questions or writing a plan file.
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

## Creative Alternatives Considered

*(Only if `butt-stallion` was consulted)*

[1-3 ideas explored, with brief notes on why the chosen approach won]

## Security Constraints

*(Only if `neo` was consulted)*

- [Security rule]

If `neo` flagged CRITICAL or HIGH findings, they are addressed in the approach above.

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
