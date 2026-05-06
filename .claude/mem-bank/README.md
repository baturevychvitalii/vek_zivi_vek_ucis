# Mem-bank Subsystem

Self-contained memory-management subsystem. Captures per-session summaries during a Claude Code session and graduates them into a durable archive when work on a topic concludes.

The subsystem is consolidated under `.claude/mem-bank/`. Outside that folder, three host-fixed locations carry thin handles that point in: `.claude/settings.json`, `.claude/commands/mem-bank-graduate.md`, and `.gitignore`. Per-instance state (the active-context file, its backups, and the graduation archive) lives wherever the instance lives — currently under `.claude/meta/` for the architect+builder shared instance.

Graduation is user-triggered (run `/mem-bank-graduate` while on the feature branch, before merging into master). The graduated `<topic>.md` then travels into master as part of the normal merge — no git hook involved.

## Subsystem files (this folder)

| Path | What |
|---|---|
| `./subscriptions.json` | Bank registry. One entry per memory bank: `name`, `bank` (directory), optional `pattern` override. Hook and graduation script both read this. |
| `./append-session-summary.py` | SessionEnd hook. Reads subscriptions, matches each bank's pattern against the transcript, spawns a single detached `claude -p` worker that appends a 2–4-sentence summary to all matched banks. |
| `./listener.py` | Transcript-scanning primitive. `read_transcript`, `extract_text`, `matches(events, patterns) -> set[str]`, `matched_any(events, patterns) -> bool`. Imported by the hook. |
| `./graduate.py` | Graduation script. In `--subscriptions` mode, iterates all banks, graduates each non-empty `small-bank.md` into `big-bank/` via Sonnet. Explicit `--source/--archive-dir/--backup-dir` mode retained for one-off use. |
| `./mem-bank.log` | Runtime log for capture and graduation. Tab-delimited. Gitignored. |
| `./last-prompt.txt` | Disk-dumped prompt the detached worker reads on spawn. Gitignored, overwritten each fire. |
| `./last-targets.txt` | Newline-delimited list of matched bank target paths written by hook, read by worker. Gitignored, overwritten each fire. |

## Bank directory convention

Each bank lives at a fixed path and follows this layout:

```
<bank>/
├── context.md       # entry point; reading it is the default trigger pattern
├── small-bank.md    # append-only session log (gitignored)
└── big-bank/        # graduation archive and backups
    └── <topic>.md
```

To register a new bank add one entry to `subscriptions.json`:
```json
{ "name": "spanish", "bank": "decks/languages/spanish" }
```
The default trigger pattern is `<bank>/context\.md`. Override with `"pattern"` for broader matching.

## Host-fixed handles (point into the subsystem)

| Path | What it does |
|---|---|
| `.claude/settings.json` | Registers the SessionEnd capture hook (`python3 .claude/mem-bank/append-session-summary.py --subscriptions .claude/mem-bank/subscriptions.json`). Allowlists `python3 .claude/mem-bank/graduate.py:*`. |
| `.claude/commands/mem-bank-graduate.md` | `/mem-bank-graduate` slash command. Runs `graduate.py --subscriptions ...` — no variables needed. |
| `.gitignore` | Ignores subsystem runtime artifacts (`mem-bank.log`, `last-prompt.txt`, `last-targets.txt`) and per-bank `small-bank.md` files. |

