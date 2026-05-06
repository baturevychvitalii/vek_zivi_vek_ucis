# Mem-bank Subsystem

Self-contained memory-management subsystem. Captures per-session summaries during a Claude Code session and graduates them into a durable archive when work on a topic concludes.

The subsystem is consolidated under `.claude/mem-bank/`. Outside that folder, three host-fixed locations carry thin handles that point in: `.claude/settings.json`, `.claude/commands/mem-bank-graduate.md`, and `.gitignore`. Per-instance state (the active-context file, its backups, and the graduation archive) lives wherever the instance lives — currently under `.claude/meta/` for the architect+builder shared instance.

Graduation is user-triggered (run `/mem-bank-graduate` while on the feature branch, before merging into master). The graduated `<topic>.md` then travels into master as part of the normal merge — no git hook involved.

## Subsystem files (this folder)

| Path | What |
|---|---|
| `./append-session-summary.py` | SessionEnd hook. Detects relevant sessions, slims transcript, spawns a detached `claude -p` worker that appends a 2–4-sentence summary to the target file. |
| `./listener.py` | Transcript-scanning primitive. `read_transcript`, `extract_text`, `matches(events, patterns) -> set[str]`, `matched_any(events, patterns) -> bool`. Imported by the hook; future consumer of the multi-instance dispatcher and graduate routing. |
| `./graduate.py` | Graduation script. Reads source, calls Sonnet for `{filename, summary}`, writes archive entry, backs up source, deletes source. |
| `./mem-bank.log` | Runtime log for capture and graduation. Tab-delimited. Gitignored. |
| `./last-prompt.txt` | Disk-dumped prompt the detached worker reads on spawn. Gitignored, overwritten each fire. |

## Host-fixed handles (point into the subsystem)

| Path | What it does |
|---|---|
| `.claude/settings.json` | Registers the SessionEnd capture hook (`python3 .claude/mem-bank/append-session-summary.py --keywords ... --target ...`). Allowlists `python3 .claude/mem-bank/graduate.py:*`. |
| `.claude/commands/mem-bank-graduate.md` | `/mem-bank-graduate` slash command. Thin wrapper that runs `graduate.py` with this instance's source/archive/backup paths. |
| `.gitignore` | Ignores subsystem runtime artifacts (`.claude/mem-bank/mem-bank.log`, `last-prompt.txt`) and per-instance state (`active-context.md`, `.archived/`). |

