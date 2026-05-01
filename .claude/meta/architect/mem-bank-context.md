# Mem-bank Infrastructure — Navigation

Index of every file involved in the mem-bank memory-management subsystem. Not auto-loaded; pull it up when working on the system.

## Capture — per-session summary → `active-context.md`

| Path | What |
|---|---|
| `.claude/hooks/mem-bank/append-session-summary.py` | SessionEnd hook. Detects relevant sessions, slims transcript, spawns a detached `claude -p` worker that appends a 2–4-sentence summary to the target file. |
| `.claude/hooks/mem-bank/mem-bank.log` | Runtime log for capture and graduation. Tab-delimited. Gitignored. |
| `.claude/hooks/mem-bank/last-prompt.txt` | Disk-dumped prompt the detached worker reads on spawn. Gitignored, overwritten each fire. |

## Graduation — `active-context.md` → `why/<topic>.md`

| Path | What |
|---|---|
| `.claude/scripts/mem-bank-graduate.py` | Graduation script. Reads source, calls Sonnet for `{filename, summary}`, writes archive entry, backs up source, deletes source. |
| `.claude/commands/mem-bank-graduate.md` | `/mem-bank-graduate` slash command. Manual trigger; thin wrapper around the script with project-specific paths. |
| `.githooks/post-merge` | Git hook. Auto-fires on `git merge` when HEAD after merge is `master` or `main`; passes the merged branch name to the script. |
| `.githooks/README.md` | One-time per-clone setup: `git config core.hooksPath .githooks`. |

## Storage

| Path | What |
|---|---|
| `.claude/meta/state/context.md` | Minimal entry point — directs readers to `active-context.md`. |
| `.claude/meta/state/active-context.md` | Branch-scoped scratchpad. Capture target and graduation source. Gitignored. |
| `.claude/meta/state/.archived/` | Pre-graduation byte-for-byte backups of `active-context.md`. Gitignored, local-only insurance. |
| `.claude/meta/architect/why/` | Durable archive. Graduation outputs land here as `<topic>.md`. |

## Wiring

| Path | What |
|---|---|
| `.claude/settings.json` | Registers the SessionEnd capture hook with `--keywords` and `--target`. Allowlists `python3 .claude/scripts/mem-bank-graduate.py:*`. |
| `.gitignore` | Ignores `mem-bank.log`, `last-prompt.txt`, `active-context.md`, `.archived/`. |

## Design records

- `.claude/meta/architect/why/mem-bank.md` — original mem-bank design rationale (legacy hand-curated).
- Future mem-bank graduations land alongside as more specific topical files (e.g., `mem-bank-hook-implementation.md`, `mem-bank-graduation.md`).
