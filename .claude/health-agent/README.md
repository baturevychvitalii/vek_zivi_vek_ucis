# Health Agent Subsystem

Self-contained observability layer. Detects builder rule violations and behavioral anomalies in skill runs, then surfaces findings at the start of the next session.

## Philosophy

This subsystem is the enforcement arm of the builder law. Think of it as a simulated framework of government, law, and the judiciary — where the law is `.claude/meta/builder/context.md`, and the health agent is the judge. It automatically detects misbehavior and proposes fixes; it may also help spot when the law itself needs mending.

## Testing

```bash
python3 .claude/health-agent/tests/test_health_agent.py
```

34 tests: 6 detector modules × unit cases + one end-to-end hook integration test.

## Subsystem files

| Path | What |
|---|---|
| `hooks/` | Hook scripts — registered in `settings.json`, fire automatically |
| `detectors/` | One Python module per builder rule; each exports `detect(ctx) -> list[dict]` |
| `tests/test_health_agent.py` | Test suite — detector units + e2e hook integration |
| `hooks.log` | Runtime log — tab-delimited, gitignored |
| `run-summary.json` | Current skill observation window — gitignored |
| `permission-events.jsonl` | Raw permission events for the current session — gitignored |
| `health-findings.jsonl` | Accumulated findings across sessions |
| `pending-ai-review.flag` | Written by detect hook; triggers the agent on next session start — gitignored |

## Host-fixed handles (point into the subsystem)

| Path | What |
|---|---|
| `.claude/settings.json` | Registers all hooks; allowlists `Write(.claude/health-agent/health-findings.jsonl)` |
| `.claude/agents/health-agent.md` | Agent definition — invoked automatically or on demand via `/health-agent` |
| `.gitignore` | Ignores runtime artifacts |
| `.claude/meta/builder/health-agent-contract.md` | Builder-side contract: every builder rule must have a detector |

## Hook reference

| Script | Trigger | What it does |
|---|---|---|
| `hooks/observe-skill-start-natural.py` | `PostToolUse(Skill)` | Records skill name + transcript path to `run-summary.json` |
| `hooks/observe-session-health.py` | `Stop` | Stamps `completed_at` and resolves pipeline spec path on `run-summary.json` |
| `hooks/detect-health-issues.py` | `Stop` | Runs all detectors; appends findings to `health-findings.jsonl`; writes `pending-ai-review.flag` |
| `hooks/surface-session-health.py` | `UserPromptSubmit` | If flag exists: triggers agent silently. Otherwise: periodic reminder if unreviewed findings exist |
| `hooks/log-permission-request.py` | `PermissionRequest` | Logs all permission events to `permission-events.jsonl` for the whitelist_gap detector |

## Data flow

```
PostToolUse(Skill)
  → observe-skill-start-natural.py    writes run-summary.json

Stop
  → observe-session-health.py         stamps completed_at on run-summary.json
  → detect-health-issues.py           runs all detectors
                                       appends findings to health-findings.jsonl
                                       writes pending-ai-review.flag if findings exist

UserPromptSubmit (next session)
  → surface-session-health.py         if flag exists: invoke agent silently
                                       if ai_processed findings exist: periodic reminder (7-day throttle)

  → health-agent (auto)               processes unreviewed findings
                                       sets status → ai_processed + verdict fields
                                       removes flag
                                       nudges user only on confirmed_violation or anomaly

/health-agent (on demand)
  → health-agent                      surfaces ai_processed findings, asks to apply fixes
                                       sets status → user_reviewed

Note: surfacing (Priority 2 reminder) only fires in builder-mode sessions. User and
architect sessions are always silent.
```

## Finding lifecycle

```
unreviewed → (agent processes) → ai_processed → (user reviews) → user_reviewed
```

## Tuning knobs

**Ignored skills** — `IGNORED_SKILLS = []` in `hooks/observe-skill-start-natural.py`. Add skill names to suppress observation.

**Detectors** — add/remove modules from `detectors/` and update `ALL_DETECTORS` in `hooks/detect-health-issues.py`. Each detector must follow the contract in `.claude/meta/builder/health-agent-contract.md`.

**Nudge threshold** — `health-agent.md` only nudges for `confirmed_violation` and `behavioral_anomaly`. Adjust the verdict condition to change sensitivity.

**Reminder mode** — `hooks/surface-session-health.py` only surfaces findings in builder-mode sessions. Change the `mode != "builder"` guard to adjust.

## Logging

Each hook writes to `hooks.log` (tab-delimited: `{timestamp}\t{tag}\t{detail}`). This is the primary debugging surface for the subsystem. There is no shared logger infrastructure yet — each hook writes directly. A future logger subsystem (one that all subsystems can request a logger from) would be the architecturally sound generalization of this pattern across mem-bank, health-agent, and the debug hooks.

## Before modifying

- Hook paths are registered in `../../settings.json` — keep in sync if you rename scripts.
- `hooks/log-permission-request.py` is health-agent's own copy; the debug hook at `.claude/hooks/debug/log-permission-request.py` writes only to the debug log.
- All hooks use `os.path.dirname(os.path.abspath(__file__))` as the anchor, so they work regardless of where Claude Code is invoked from.
