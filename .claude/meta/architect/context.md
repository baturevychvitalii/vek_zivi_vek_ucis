# Design Philosophy

*Read this when making architectural decisions — new features, structural changes, or
anything that shapes how the system grows. Not for everyday card operations.*

---

## What This Project Actually Is

The output of this project is not an executable file or a deployed service.
**The output is a running instance of Claude that is already fully capable.**

Skills, pipelines, hooks, and context files are the interfaces through which that
capability is directed — not the capability itself. Every design decision should
preserve this: the human + Claude pair, empowered by well-structured context, is the
end state. There is no further layer needed.

---

## The Skill Being Practiced Here

This project is a sandbox for **context engineering** — the discipline of shaping what
Claude knows, when it knows it, and how reliably it acts on that knowledge.

The flashcard use case is real, but it is also the petri dish. The goal is to develop
fluency in:

- Designing context packages that load exactly when needed, not more
- Building governance that enforces itself (hooks > manual review)
- Making Claude's behavior observable and verifiable, not just assumed
- Understanding where mechanical enforcement is necessary vs. where navigation suffices

Each architectural decision is also a hypothesis about how Claude behaves. Treat gaps
and failures as data, not just bugs.

---

## The Non-Duplication Principle

**If something exists somewhere, it shall be reused or made automatically reusable —
never repeated.**

This applies at every level:
- Skills are generic so a new domain needs only a context file, not a new skill
- If a rule is in its canonical location, it is not also here or in CLAUDE.md
- If a decision is documented in `why/`, it is not re-explained elsewhere
- If a pattern is in the stdlib, new pipelines compose it — they don't inline it

Duplication is a signal that something hasn't found its canonical home yet.
When you notice it, consolidate — don't patch both copies.

---

## Core Pattern

```
generic skill + context file = specialized behavior
```

Skills are thin orchestration. All domain intelligence lives in context files.
The context files *are* the programs. Adding a new domain requires only a new context
file — no skill changes. This composability is the architecture's primary invariant.
Protect it.

The same principle extends to the project structure itself: new modes, new domains,
new governance layers should all slot in without modifying what already works.

---

## Design Principles

**Composability over monoliths**
New capabilities should slot in without modifying existing skills or pipelines.
If a new feature requires changing a generic skill, the context file isn't carrying
enough of the domain logic.

**Governance contracts are first-class**
Authoring rules, security constraints, and operational policies each have a single
canonical location. When a new contract is needed, find or create its home — don't
scatter it. Everything else references, never repeats.

**Context by navigation, not injection (where reliable)**
Prefer explicit "read X before proceeding" instructions over hook-forced injection.
Navigation makes compliance observable. Injection makes it invisible.
Use enforcement only where navigation demonstrably fails and the cost of the gap is high.

**Token economics: lazy-load heavy context**
Always-loaded context should be minimal. Heavy context loads on demand.
Any growing file is a candidate for splitting into a thin handle and a full spec.
Apply this pattern wherever context accumulates.

**Observability before trust**
The hooks layer is a feedback loop, not just an audit log. Observable compliance is
more valuable than invisible enforcement. Design for the ability to see what happened.

---

## Modes of Operation

Three distinct modes require different context. They must not bleed into each other.

**User mode** — operational context only. The user is adding cards, running pipelines,
using the system. Architectural context should not be present.

**Builder mode** — extending current infrastructure along established patterns.
The entry points are the governance contracts (for modifying skills/pipelines) and
domain context files (for modifying decks). No architectural decisions needed.

**Architect mode** — you are here. Changing how the system grows: new layers,
new primitives, new governance patterns, reconsidering structure.
Read the historical arc (`why/trajectory-snapshot.md`) alongside this file.

---

## Layer Responsibilities

The system has distinct layers. Each layer has a single responsibility and a direction
of dependency — upper layers know about lower layers, never the reverse.

- **Domain packages** — carry their own rules and behavior; the system reads from them
- **Stdlib (skills)** — generic operations; read from packages, know nothing about pipelines
- **Application layer (pipelines)** — orchestrate skills with error handling; no inline logic
- **Enforcement layer (hooks)** — enforce contracts at write time; independent of content
- **Constitution (meta/)** — design record and governance; referenced, never modified lightly

Collapsing layers for convenience is always a short-term gain and a long-term cost.

---

*Historical arc: `.claude/meta/architect/why/`*
*Authoring contracts: `.claude/meta/builder/security.md`*
