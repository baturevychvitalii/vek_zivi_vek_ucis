# Meta State

Stateful context for **architect** and **builder** modes — what the project is becoming
and what is in flight on this branch. User mode never reads this directory.

## Files

- **`product-vision.md`** *(committed)* — forward-looking north star. Updated by architect
  mode when project direction shifts.
- **`active-context.md`** *(gitignored)* — current development focus, open threads, where
  to resume. Scratchpad — overwritten per session, not appended. Lives only in the local
  checkout; disappears when the branch is merged and the worktree is removed.

## The Pattern

This is the **meta instance** of a stateful-context pattern that pairs a static half
(identity, vision — committed) with a dynamic half (current state — often gitignored).

The same pattern recurs at the area level (currently `decks/`, rename to `areas/`
pending): `inheritable-*.md` files are the static half, and an area-level `state/`
subdirectory holds whatever dynamic state the area needs (e.g., the lit_search reading
log). Meta state and area state are **siblings** — same shape, different audiences,
different writers. They do not share files; neither inherits from the other.

## Lifecycle

**Read** — navigation-based, not hook-injected. The pointers in `architect/context.md`
and `builder/context.md` direct the agent here when entering those modes.

**Update** — agent-driven by convention. Both mode `context.md` files instruct the agent
to update `active-context.md` before finishing a session. No automation; if the session
ends abruptly the update is missed — acceptable trade-off for v1.

## What Belongs Here vs. Elsewhere

| Information | Goes to |
|---|---|
| Project's evolving purpose / direction | `product-vision.md` (here) |
| Current focus, open threads, blockers | `active-context.md` (here) |
| Finalized architectural decisions | `meta/architect/why/` |
| Frozen point-in-time retrospectives | `meta/architect/why/` (e.g. trajectory-snapshot) |
| Tech stack, file map, navigation | `CLAUDE.md` + the inheritable cascade |
| Per-area learning state | `<area>/state/` |
| Operational findings from skill runs | health_agent subsystem |

`active-context.md` is **not a decision log** — anything worth keeping permanently
graduates to `why/` before the branch closes.
