Back up a single Anki deck to a dated .apkg file.

Usage: `/skill:anki-backup-deck <deck>` — e.g. `/skill:anki-backup-deck spanish` or `/skill:anki-backup-deck spanish/dialects/rioplatense`

`<deck>` is a path of any depth under `decks/` — the skill reads the context.md at that location.

## Step 0 — Resolve Deck Config

Read `decks/<deck>/context.md` (following context-inheritance: walk up from `decks/` to the target, reading each `context.md` root-first). Extract:
- `deckName` (e.g. `"Español"`)

Derive variables:
- `CONTEXT_DIR` = `decks/<deck>` (the directory containing the deck's context.md)
- `BACKUP_DIR` = `<CONTEXT_DIR>/backups`

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

```bash
python3 .claude/anki.py '{"action": "exportPackage", "params": {"deck": "<deckName>", "path": "<PROJECT_ROOT>/<BACKUP_DIR>/<FILENAME>", "includeSched": true}}'
```

Parse the result:
- `result["result"] == true` → success
- `result["result"] == false` or error present → report the error and stop

## Step 3 — Report

```
✓ <deckName> backed up → <BACKUP_DIR>/<FILENAME>
```
