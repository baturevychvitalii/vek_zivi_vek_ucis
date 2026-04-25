# Health Agent — Tuning Context

Read this before modifying any part of the health-agent subsystem.

## Philosophy and direction (this paragraph is written by hand and shall be adhered to with most attention)
From the philosophical/architectural point of view - this subsystem shall be the organ that makes sure all `builder`
guidelines are adhered to. 
Think of it as a simulated framework of government, law, and the judiciary.
Where the law is .claude/meta/builder/context.md.
The health agent is the judge.

It shall automatically detect 'misbehavior' and propose fixes. Maybe help me, the architect, spot that the law shall be mended.

## What this system actually does as of now

Practically Observes skill runs, detects tool errors and unexpected permission prompts,
accumulates findings, and surfaces them to the user on demand.

## Entry points

| File | What it does |
|---|---|
| `HOOKS.md` | Hook-by-hook reference: triggers, inputs, outputs |
| `../../agents/health-agent.md` | Agent definition: how findings are analyzed and reported |
| `../../agents/health-agent/health-findings.jsonl` | Accumulated findings (runtime) |
| `../../agents/health-agent/health-state.json` | Nudge throttle state (runtime) |

## Tunable knobs

**Ignored skills** — `observe-skill-start.py` and `observe-skill-start-natural.py`
each have an `IGNORED_SKILLS = []` list. Add skill names here to suppress observation
for specific pipelines.

**Permission prompt filtering** — `detect-health-issues.py` filters out any prompt
whose `detail` contains `/.claude/` or starts with `.claude/`. Extend this logic
to suppress false positives from known-safe tools.

**Nudge throttle** — `surface-session-health.py` waits 7 days between nudges.
Change `timedelta(days=7)` to adjust cadence.

**Finding TTL** — findings accumulate indefinitely. Consider adding a cleanup pass
in `detect-health-issues.py` or the agent to expire old processed entries.

## Runtime files (not committed)

| File | Written by | Read by |
|---|---|---|
| `run-summary.json` | observe-skill-start, observe-skill-start-natural | observe-session-health, detect-health-issues |
| `permission-events.jsonl` | log-permission-request.py  | detect-health-issues |
| `hooks.log` | observe-skill-start-natural | debug inspection |

## Data flow

```
UserPromptSubmit / PostToolUse(Skill)
  → observe-skill-start*.py        writes run-summary.json

Stop
  → observe-session-health.py      stamps completed_at on run-summary.json
  → detect-health-issues.py        reads summary + transcript + permission-events
                                   appends findings to health-findings.jsonl

UserPromptSubmit (next session)
  → detect-health-issues.py        analyzes previous run if unanalyzed
  → surface-session-health.py      nudges user if unreviewed findings exist

on-demand
  → health-agent                   reads findings, diagnoses, proposes fixes
```

## Before modifying

- Hook paths are registered in `../../settings.json` — keep in sync if you rename files.
- `log-permission-request.py` here is health-agent's own copy; the generic one at
  `../log-permission-request.py` writes only to `../hooks.log` for session-wide auditing.
- All paths in hooks use `os.path.dirname(os.path.abspath(__file__))` as the base,
  so they work regardless of where Claude Code is invoked from.
