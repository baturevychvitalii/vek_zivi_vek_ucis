# Why: Pipeline Health Agent

*Added 2026-04-24.*

---

## The Problem

Pipeline runs in user mode periodically hit friction — permission prompts, skill
failures, unexpected interruptions. The problems were diagnosed manually, patched
once, and then recurred as pipelines evolved. No feedback loop existed.

The recurring pattern: a new script gets added to a skill spec but its `settings.json`
allow entry is forgotten. Or a command uses an absolute path where the whitelist
expects relative. Or a skill fails silently. Each instance was a one-off fix with
no institutional memory.

---

## The Solution

A lightweight feedback loop built in three layers:

**Hook layer (detection):** Two `UserPromptSubmit` hooks and one `Stop` hook bracket
every slash-command invocation. `observe-skill-start.py` fires when a `/` prompt is
submitted, writes a `run-summary.json` with the skill name and session transcript path.
`observe-session-health.py` fires when the turn ends, adds the pipeline spec path and
completion timestamp. `surface-session-health.py` fires at the start of the next
session and, if a pending summary exists, injects a reminder for Claude to invoke
the health agent.

**Subagent layer (analysis):** `health-agent` (`.claude/agents/health-agent.md`) is
a Haiku-model Claude Code subagent with project-scoped persistent memory. When invoked,
it reads the session transcript and pipeline spec, identifies deviations from the
expected flow, diagnoses root causes, and proposes minimal fixes. It never writes to
`settings.json` or skill specs directly — it surfaces proposals for user approval.

**Memory layer (accumulation):** The subagent's memory at `.claude/agent-memory/health-agent/`
builds institutional knowledge across sessions — recurring patterns, fixes that worked,
fragile pipeline steps. Each analysis adds to this, so the agent becomes more useful
over time rather than starting cold on every invocation.

---

## Design Decisions

**Hook detects, subagent analyzes.** A hook script cannot reason about "why did this
fail?" — it can only detect that something happened. A subagent can read context, compare
expected vs. actual, and produce a diagnosis. The two layers do different jobs and
should stay separate.

**All skills watched by default, blacklist for exceptions.** The original instinct was
a whitelist of "important" skills. Inverted: any slash command triggers observation,
and `IGNORED_SKILLS` allows opting out. New pipelines are covered automatically.

**Next-session notification, not same-session interruption.** The analysis surfaces at
the start of the next session, not immediately after the pipeline ends. This avoids
interrupting a pipeline run mid-flow and matches the natural "what happened last time?"
question that opens most sessions.

**No `claude -p` in hooks.** Background Claude invocations from hooks have credential
friction in this environment. The subagent runs inside the regular session where
credentials are already resolved.

**`user_experience.md` is generic, not agent-specific.** The UX principles (smoothness
checklist, path format rules, what "friction" means) belong in builder-mode context,
not inside the agent. The agent's system prompt has its own task-specific instructions.
The generic document educates any builder-mode session working on pipelines.

---

*Files: `.claude/agents/health-agent.md` · `.claude/hooks/observe-skill-start.py` ·
`.claude/hooks/observe-session-health.py` · `.claude/hooks/surface-session-health.py` ·
`.claude/meta/builder/user_experience.md`*
