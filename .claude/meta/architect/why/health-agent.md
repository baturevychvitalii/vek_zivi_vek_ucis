# Why: Pipeline Health Agent

*Added 2026-04-24. Substantially revised 2026-04-27.*

---

## The Problem

Pipeline runs periodically hit friction — permission prompts, skill failures, unexpected
interruptions. The problems were diagnosed manually, patched once, and then recurred as
pipelines evolved. No feedback loop existed.

The recurring pattern: a new script gets added to a skill spec but its `settings.json`
allow entry is forgotten. Or a command uses an absolute path where the whitelist expects
relative. Or a skill fails silently. Each instance was a one-off fix with no institutional
memory.

---

## The Solution

A lightweight feedback loop built in three layers:

**Hook layer (detection):** Hooks bracket every skill invocation. `observe-skill-start-natural.py`
fires on `PostToolUse(Skill)`, writing a `run-summary.json` with the skill name and
transcript path. `observe-session-health.py` fires on `Stop` to stamp `completed_at`.
`detect-health-issues.py` runs detector modules against the session transcript and
accumulates structured findings. `surface-session-health.py` injects a reminder into
the next session's context when findings are pending.

**Subagent layer (analysis):** `health-agent` (`.claude/agents/health-agent.md`) is a
Haiku-model subagent. It reads accumulated findings, loads only the relevant builder law
sections per finding, produces structured verdicts, and surfaces a nudge only on confirmed
violations or anomalies. It proposes fixes but never applies them without user approval.

**Detector layer (rules):** One Python module per builder rule in `detectors/`. Each
exports `detect(ctx) -> list[dict]`. The contract (`health-agent-contract.md`) requires
every builder rule to have a complementing detector — a rule without a detector is
unenforceable.

---

## Design Decisions

**Hook detects, subagent analyzes.** A hook script cannot reason about "why did this
fail?" — it can only detect that something happened. A subagent can read context, compare
expected vs. actual, and produce a diagnosis. The two layers do different jobs and
must stay separate.

**`observed-skill-start-natural.py` over `observe-skill-start.py`.** The original design
watched for slash commands on `UserPromptSubmit`. This was wrong — the system is invoked
in natural language ("add to spanish deck…") and the Skill tool fires mid-turn, not as a
prompt. `PostToolUse(Skill)` is the correct observation point. The slash-command watcher
remains as a fallback but is no longer the primary signal.

**`detect-health-issues.py` must be unconditional.** An early design guarded on
`prompt.startswith("/")`, so detection only ran after slash commands. Natural language
sessions were invisible to the health agent. Removing the guard was the fix: the
`analyzed_at` sentinel in `run-summary.json` already prevents double-analysis.

**Next-session notification, not same-session interruption.** Analysis surfaces at the
start of the next session. This avoids interrupting a pipeline run mid-flow and matches
the natural "what happened last time?" question that opens most sessions.

**No `claude -p` in hooks.** Background Claude invocations from hooks have credential
friction in this environment. The subagent runs inside the regular session where
credentials are already resolved.

**Trigger logs on every hook.** After repeated failures that were hard to diagnose — hooks
firing silently, detection not running, flags never being set — every hook script now
writes to `hooks.log`. The log is the primary debugging surface for the subsystem itself.

---

## The Debug Loop

Building this subsystem exposed a class of problem specific to context-engineering
applications: **the debug loop is long and lossy**.

In a normal software project, a failing test gives you immediate feedback — the loop
is seconds. Here, the loop spans sessions: a pipeline runs, something goes wrong, the
hook tries to capture it, detection fires (or doesn't), the next session starts, the
agent processes findings (or doesn't), a nudge surfaces (or doesn't). Each step has
failure modes that are invisible without explicit logging, and a bug at step 2 means
you learn nothing from steps 3 through 6.

Concretely: the detection script had a slash-command guard. Every natural-language
session was silently dropping findings. The symptom — "health agent never notified me" —
was correct but the cause was buried two layers down in a guard clause that made sense
at the time it was written (the system was designed for slash commands) but became wrong
as the invocation model changed. There was no indication that the guard was the issue
until the transcript was read directly and compared to the code path.

This is a pattern: **the assumption that was correct at design time becomes the bug as
the system evolves, and the system has no mechanism to surface that the assumption is
now violated.** The health agent itself is an attempt to address this for builder rules.
But the health agent's own infrastructure had no equivalent — it was the cobbler's
shoeless children.

Trigger logs on every hook are the minimal fix. But the deeper lesson is architectural:
context-engineering applications need explicit observability at every layer boundary,
because the feedback loop is too long to debug by feel.

---

## What's Next (as of 2026-04-27)

The recurring debug loop — and the specific experience of spending sessions diagnosing
infrastructure that should be self-diagnosing — prompted a shift in thinking. Rather than
continuing to iterate on this subsystem in the same channel, the next work will happen
at a higher layer of abstraction: frameworks for memory banks, structured debugging
approaches, and observability patterns specific to context-engineering applications.

The health agent as built is a working first iteration. Its limitations are now documented
here. Further architectural evolution belongs in that separate channel.

---

*Files: `.claude/agents/health-agent.md` · `.claude/hooks/health-agent/` ·
`.claude/meta/builder/health-agent-contract.md`*
