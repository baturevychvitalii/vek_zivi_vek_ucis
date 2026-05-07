# Mem-bank Subsystem

Self-contained memory-management subsystem. Captures per-session summaries during a Claude Code session and graduates them into a durable archive when work on a topic concludes.

The subsystem is consolidated under `.claude/mem-bank/`. Outside that folder, three host-fixed locations carry thin handles that point in: `.claude/settings.json`, `.claude/commands/mem-bank-big-bank.md`, and `.gitignore`. Per-instance state (the active-context file, its backups, and the graduation archive) lives wherever the instance lives — currently under `.claude/meta/` for the architect+builder shared instance.

Graduation is user-triggered (run `/mem-bank-big-bank` while on the feature branch, before merging into master). The graduated `<topic>.md` then travels into master as part of the normal merge — no git hook involved.

## Subsystem files (this folder)

| Path | What |
|---|---|
| `./subscriptions.json` | Bank registry. One entry per memory bank: `name`, `bank` (directory), optional `pattern` override. Graduation script reads this. |
| `./registry.py` | Bank registry primitive. `load_banks`, `bank_effective_patterns`, `bank_small_bank_path`, `bank_archive_dir`, `populated_banks`. Imported by `small-bank.py` and `big-bank.py`. |
| `./small-bank.py` | SessionEnd hook. Reads subscriptions, matches each bank's pattern against the transcript, spawns a single detached `claude -p` worker that appends a 2–4-sentence summary to all matched banks. |
| `./big-bank.py` | Graduation script. In `--subscriptions` mode, iterates all banks, graduates each non-empty `small-bank.md` into `big-bank/` via Sonnet. Explicit `--source/--archive-dir/--backup-dir` mode retained for one-off use. |
| `./mem-bank.log` | Runtime log for capture and graduation. Tab-delimited. Gitignored. |
| `./last-jobs.json` | JSON array of `{"target", "prompt"}` jobs written by hook, read by worker. One entry per matched bank. Gitignored, overwritten each fire. |

## Bank directory convention

Each bank lives at a fixed path and follows this layout:

```
<bank>/
├── context.md           # entry point; reading it is the default trigger pattern
├── this-bank-prompt.md  # optional: per-bank capture filter (see below)
├── small-bank.md        # append-only session log (gitignored)
└── big-bank/            # graduation archive and backups
    └── <topic>.md
```

To register a new bank add one entry to `subscriptions.json`:
```json
{ "name": "spanish", "bank": "decks/languages/spanish" }
```
The default trigger pattern is `<bank>/context\.md`. Override with `"patterns"` for broader matching.

### Per-bank capture filter (`this-bank-prompt.md`)

If `this-bank-prompt.md` is present in the bank directory, its contents are injected into the summarization prompt as a `BANK FILTER` rule — evaluated before the session data. Use it to exclude irrelevant sessions from a bank.

The filter instruction should describe what qualifies for capture. The script automatically appends: *"If this filter excludes the session, respond with exactly SKIP."* Workers that receive `SKIP` log the exclusion and skip appending.

Example (`decks/languages/spanish/reading-log/this-bank-prompt.md`):
```
This is the Spanish reading history bank. Only capture if the session involved
selecting a book to read or reporting back on a completed book. Sessions about
card creation or vocabulary should be excluded.
```

## Host-fixed handles (point into the subsystem)

| Path | What it does |
|---|---|
| `.claude/settings.json` | Registers the SessionEnd capture hook (`python3 .claude/mem-bank/small-bank.py --subscriptions .claude/mem-bank/subscriptions.json`). Allowlists `python3 .claude/mem-bank/big-bank.py:*`. |
| `.claude/commands/mem-bank-big-bank.md` | `/mem-bank-big-bank` slash command. Runs `big-bank.py --subscriptions ...` — no variables needed. |
| `.gitignore` | Ignores subsystem runtime artifacts (`mem-bank.log`, `last-jobs.json`) and all `small-bank.md` files via `**/small-bank.md`. |

## Merge dynamics

Small-bank and big-bank have different persistence models:

| | `small-bank.md` | `big-bank/<topic>.md` | `big-bank/small-bank-archive/` |
|---|---|---|---|
| Tracked in git | No (gitignored) | Yes | Yes |
| Travels with merges | No | Yes | Yes |
| Touched by branch switch | No | Yes | Yes |

**Small-bank is local-only.** Git never touches it — no merge conflicts, no accidental deletion via merge. It lives only on the current machine's working tree until graduation.

**The workflow is: develop → graduate → merge.**

1. Develop on a feature branch. SessionEnd captures summaries into `small-bank.md`.
2. Before merging, run `/mem-bank-big-bank`. This graduates `small-bank.md` into `big-bank/<topic>.md`, archives it to `big-bank/small-bank-archive/`, and deletes `small-bank.md`.
3. Commit the new big-bank files and merge. The graduated entries travel into master normally.

**If you merge without graduating first:** your ungraduated small-bank entries are not lost — they survive on disk (git doesn't touch gitignored files). Run graduation at any point to recover them. The only way to lose them is `git clean -fdx`.

