# Structural Lessons

Distilled from incidents in this project's own history (see `../memory/big-bank/`).
Each lesson traces to a real failure or convergence — they describe the shape every
subsystem here has converged on.

**Orchestrator + isolated worker + artifact.**
Python handles deterministic mechanics (I/O, process management, state); the AI worker
(`claude -p --bare`) handles judgment; the artifact carries output and is the interface
between components. mem-bank and compiled-context generation both converged here.
New AI-powered subsystems should fit this shape.

**Structural isolation beats behavioral rules.**
Rules can be skipped; process boundaries cannot. When isolation matters, use a
subprocess with explicit context passing — not a navigation instruction. Reference:
compiled-context flattens the inheritance chain to one file and passes it to a bare
subprocess with no access to CLAUDE.md, memory, or hooks.

**Silent failure is this system's default failure mode.**
Feedback loops here are long and lossy: an assumption correct at design time silently
becomes the bug. Observability is a contract, not a courtesy — every hook and worker
writes a trigger log as its primary debugging surface, and lifecycle-boundary code
fails open (log + exit 0, never block teardown). Evidence: health-agent, the 161KB
argv overflow, the small-bank gitignore data loss.

**Events re-fire; producers must be idempotent.**
SessionEnd fires again on /compact, workers rerun, merges re-propagate files.
Append-only artifacts require producers that replace by identity key, not blindly
append. Reference: small-bank's unprocessed-job replace keyed on session_id + target.

**Every process boundary has a limit — enumerate before building.**
argv caps (128KiB), Bash timeouts, /tmp bans, merge semantics: each became
architecture only after a silent collision. Before building on a substrate, list its
sizes, timeouts, and delivery semantics next to the design; cap anything that crosses
a boundary (reference: `_elide` / PROMPT_CAP in small-bank).

**Two-tier memory is a project primitive.**
Accumulating state gets a cheap raw capture tier — branch-local, gitignored,
append-only — and a deliberate graduation tier — curated, committed. Git carries only
graduated artifacts; mutable runtime state never crosses a merge.
(small-bank → big-bank; health findings → review; reading-log.)

**Design interfaces for their reader.**
LLM-facing interfaces emit semantic tokens (FRESH / STALE / BROKEN_INCLUDE), not exit
codes — LLMs follow text. Wire protocols use layer-neutral names (`fields`, not
`new_fields`) so layers evolve independently.
