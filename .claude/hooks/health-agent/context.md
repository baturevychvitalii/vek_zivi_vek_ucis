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

Observes skill runs, runs Python detectors for specific builder rule violations and
behavioral anomalies, accumulates structured findings, then triggers the health-agent
to analyze findings silently at the start of the next session. Nudges the user only
when a real issue is found.

## Entry points

| File | What it does |
|---|---|
| `HOOKS.md` | Hook-by-hook reference: triggers, inputs, outputs |
| `../../agents/health-agent.md` | Agent definition: verdict logic, output format |
| `detectors/` | One Python module per builder rule; each exports `detect(ctx)` |
| `../../meta/builder/health-agent-contract.md` | Contract: every new builder rule needs a detector |
| `../../agents/health-agent/health-findings.jsonl` | Accumulated findings (runtime) |
| `../../agents/health-agent/health-state.json` | Reminder throttle state (runtime) |

## Data flow

```
UserPromptSubmit / PostToolUse(Skill)
  → observe-skill-start*.py        writes run-summary.json

Stop
  → observe-session-health.py      stamps completed_at on run-summary.json
  → detect-health-issues.py        reads transcript + permission-events
                                   runs all detectors in detectors/
                                   appends findings to health-findings.jsonl
                                   writes pending-ai-review.flag if findings exist

UserPromptSubmit (next session)
  → surface-session-health.py      if flag exists: inject agent trigger (immediate)
                                   if ai_processed findings exist: periodic reminder (7-day throttle)

  → health-agent (auto)            processes unreviewed findings silently
                                   sets status → ai_processed + verdict fields
                                   removes flag
                                   nudges user only if confirmed_violation or anomaly

on-demand (/health)
  → health-agent                   surfaces ai_processed findings, asks to apply fixes
                                   sets status → user_reviewed
```

## Finding lifecycle

```
unreviewed → (agent processes) → ai_processed → (user reviews via /health) → user_reviewed
```

## Tunable knobs

**Ignored skills** — `observe-skill-start.py` and `observe-skill-start-natural.py`
each have an `IGNORED_SKILLS = []` list. Add skill names to suppress observation.

**Detectors** — add/remove modules from `detectors/` and update `ALL_DETECTORS`
in `detect-health-issues.py`. Each detector must follow the contract in
`../../meta/builder/health-agent-contract.md`.

**Nudge threshold** — `health-agent.md` only nudges for `confirmed_violation` and
`behavioral_anomaly` verdicts. Adjust the verdict condition to change sensitivity.

**Reminder cadence** — `surface-session-health.py` uses `timedelta(days=7)` for
the periodic "you have N unreviewed findings" reminder. Adjust to taste.

## Runtime files (not committed)

| File | Written by | Read by |
|---|---|---|
| `run-summary.json` | observe-skill-start, observe-skill-start-natural | observe-session-health, detect-health-issues |
| `permission-events.jsonl` | log-permission-request.py | detect-health-issues |
| `pending-ai-review.flag` | detect-health-issues | surface-session-health, health-agent |
| `hooks.log` | observe-skill-start-natural | debug inspection |

## Before modifying

- Hook paths are registered in `../../settings.json` — keep in sync if you rename files.
- `log-permission-request.py` here is health-agent's own copy; the generic one at
  `../log-permission-request.py` writes only to `../hooks.log` for session-wide auditing.
- All paths in hooks use `os.path.dirname(os.path.abspath(__file__))` as the base,
  so they work regardless of where Claude Code is invoked from.
- False-positive filter uses `os.path.relpath()` to normalize absolute paths before
  checking for `.claude/` prefix — covers both relative and absolute path forms.
