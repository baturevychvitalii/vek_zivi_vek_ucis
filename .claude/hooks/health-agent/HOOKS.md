# Health Agent Hooks

Enforcement-layer observers that feed the health agent. All fire automatically via
settings.json; none require manual invocation.

## observe-skill-start.py
**Trigger:** UserPromptSubmit  
Records the start of a slash-command skill run (e.g. `/pipe:anki-add-cards`) into
`run-summary.json`. Entry point for the skill-scoped observation window.

## observe-skill-start-natural.py
**Trigger:** PostToolUse(Skill)  
Same as above but for skills invoked naturally via the `Skill` tool rather than a
slash command. Writes to the same `run-summary.json`.

## observe-session-health.py
**Trigger:** Stop  
Stamps `completed_at` on the current `run-summary.json` and resolves the matching
pipeline spec path, if any. Closes the observation window for the finished run.

## detect-health-issues.py
**Trigger:** Stop + UserPromptSubmit (slash commands only)  
Reads the closed `run-summary.json`, scans the session transcript for tool errors,
and checks `permission-events.jsonl` (written by `../log-permission-request.py`) for
unexpected permission prompts. Appends findings to `../../agents/health-agent/health-findings.jsonl`.

## surface-session-health.py
**Trigger:** UserPromptSubmit  
Checks `health-findings.jsonl` for unreviewed entries. If any exist and at least
7 days have passed since the last nudge, injects a one-sentence advisory into the
Claude context via `hookSpecificOutput`.

## Runtime files (not committed)
| File | Written by | Read by |
|---|---|---|
| `run-summary.json` | observe-skill-start, observe-skill-start-natural | observe-session-health, detect-health-issues |
| `hooks.log` | observe-skill-start-natural | (debug inspection) |
| `../permission-events.jsonl` | log-permission-request.py | detect-health-issues |
