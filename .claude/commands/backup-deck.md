Back up a single Anki deck to a dated .apkg file.

Usage: `/backup-deck <deck>` — e.g. `/backup-deck spanish`

## Step 0 — Resolve Deck Config

Read `decks/<deck>/context.md`. Extract:
- `deckName` (e.g. `"Español"`)

Determine `PROJECT_ROOT` and `TODAY`:
```bash
echo "$(pwd)" && date +%Y-%m-%d
```

## Step 1 — Determine Filename

Check if `decks/<deck>/backups/<TODAY>.apkg` already exists:
```bash
ls decks/<deck>/backups/<TODAY>.apkg 2>/dev/null
```

- If it does **not** exist: use `<TODAY>.apkg`
- If it **does** exist: append a short poetic suffix drawn from Homer's Iliad (2–3 memorable words, lowercase, hyphen-separated — e.g. `2026-04-15-rosy-fingered-dawn.apkg`). Pick something fitting; no two backups should feel the same.

## Step 2 — Ensure Backup Directory Exists

```bash
mkdir -p decks/<deck>/backups
```

## Step 3 — Export

```bash
python3 .claude/anki.py '{"action": "exportPackage", "params": {"deck": "<deckName>", "path": "<PROJECT_ROOT>/decks/<deck>/backups/<FILENAME>", "includeSched": true}}'
```

Parse the result:
- `result["result"] == true` → success
- `result["result"] == false` or error present → report the error and stop

## Step 4 — Report

```
✓ <deckName> backed up → decks/<deck>/backups/<FILENAME>
```
