---
name: anki-backup-deck
description: Back up a single Anki deck to a dated .apkg file
disable-model-invocation: true
---

Back up a single Anki deck to a dated .apkg file.

Usage: `/anki-backup-deck <deck>` — e.g. `/anki-backup-deck spanish` or `/anki-backup-deck spanish/dialects/rioplatense`

`<deck>` is a path of any depth under `decks/` — the skill reads the context.md at that location.

## Step 0 — Resolve Deck Config

Read `context.md` of a specific deck from `CLAUDE.md` roadmap. Extract:
- `deckName` (e.g. `"Español"`)

Derive variables:
- `BACKUP_DIR` = `dirname(context.md)/backups`

Determine `PROJECT_ROOT`:
```bash
pwd
```

Determine `TODAY`:
```bash
date +%Y-%m-%d
```

## Step 1 — Determine Filename

Check if `<BACKUP_DIR>/<TODAY>.apkg` already exists:
```bash
ls <BACKUP_DIR>/<TODAY>.apkg 2>/dev/null
```

- If it does **not** exist: use `<TODAY>.apkg`
- If it **does** exist: append a short poetic suffix drawn from Homer's Iliad (2–3 memorable words, lowercase, hyphen-separated — e.g. `2026-04-15-rosy-fingered-dawn.apkg`). Pick something fitting; no two backups should feel the same.

## Step 2 — Export

Call `mcp__anki__export_deck` with:
- `deck`: `<deckName>`
- `path`: `<PROJECT_ROOT>/<BACKUP_DIR>/<FILENAME>` (absolute path)
- `include_sched`: `true`

On error: report the error and stop.

## Step 3 — Report

```
✓ <deckName> backed up → <BACKUP_DIR>/<FILENAME>
```
