Find all PURPLE-flagged cards in Anki, show them for confirmation, then permanently delete them from Anki and from the source files.

## Step 0 — Build Deck Map

Before doing anything else, scan `decks/` subdirectories and read `context.md` from each one.
For each deck extract the Deck Config block:
- `deckName` (the Anki deck name, e.g. "Español")
- `basicFile` (path to the basic/production cards file)
- `clozeFile` (path to the cloze cards file)

Build a lookup table: `deckName → {basicFile, clozeFile}`. This replaces any hardcoded mapping.

## Step 1 — Find PURPLE-flagged Cards

Run each command and parse the JSON output printed to stdout.

Find PURPLE-flagged cards (flag:7):
```bash
python3 .claude/anki.py '{"action": "findCards", "params": {"query": "flag:7"}}'
```
→ `result["result"]` is `card_ids` (list of integers).

If no card IDs: report "No PURPLE-flagged cards found." and stop.

Fetch card details (substitute actual IDs):
```bash
python3 .claude/anki.py '{"action": "cardsInfo", "params": {"cards": [<card_ids>]}}'
```
→ `result["result"]` is the list of card objects.

Extract `note_ids` as the deduplicated list of `card["note"]` values.

Fetch note details:
```bash
python3 .claude/anki.py '{"action": "notesInfo", "params": {"notes": [<note_ids>]}}'
```
→ `result["result"]` is the list of note objects. Build a `notes` dict keyed by `noteId`.

## Step 2 — Show Deletion List

For each card collect:
- `note_id`: `card["note"]`
- `deck`: `card["deckName"]`
- `model`: `card["modelName"]`
- `front`: `note["fields"]["Front"]["value"]` for Basic, or `note["fields"]["Text"]["value"]` for Cloze

Display:

```
About to permanently delete N card(s):

  1. [Deck] [Model] — [front text, truncated to 70 chars]
  2. ...

This cannot be undone. Confirm? [yes / no]
```

## Step 3 — Delete

On confirmation:

**Delete from Anki** (removes notes and all associated cards, substitute actual IDs):
```bash
python3 .claude/anki.py '{"action": "deleteNotes", "params": {"notes": [<note_ids>]}}'
```

**Remove from source files** — use the deck map from Step 0 to resolve the file:
- look up `card["deckName"]` in the deck map
- `model == "Basic"` → use `basicFile`; `model == "Cloze"` → use `clozeFile`

For each card, find the line where col1 matches the front/text field (split on ` | `) and delete that line. Do not leave blank lines.

Use Python to rewrite each affected file without the deleted lines:
```python
with open(filepath, "r") as f:
    lines = f.readlines()
lines = [l for l in lines if not l.startswith(front_to_delete + " |")]
with open(filepath, "w") as f:
    f.writelines(lines)
```

If the deck is not in the map (unknown deck): still delete from Anki, but warn "deck not in map — skipped file update."
If a card's line is not found in the source file: still delete from Anki, but warn "not found in source file."

## Step 4 — Report

```
Deleted N card(s):
  ✓ [front snippet] — removed from Anki and [filename]
  ⚠ [front snippet] — removed from Anki, not found in source file
```
