Find all PURPLE-flagged cards in Anki, show them for confirmation, then permanently delete them from Anki.

## Step 0 — Build Deck Map

Before doing anything else, scan `decks/` subdirectories and read `context.md` from each one.
For each deck extract the Deck Config block:
- `deckName` (the Anki deck name, e.g. "Español")

Build a lookup table of known `deckName` values. This is used for display and to identify which deck a card belongs to.

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
- Display output according to deck's `context.md`.

```
About to permanently delete N card(s):
This cannot be undone. Confirm? [yes / no]
```

## Step 3 — Delete

On confirmation:

**Delete from Anki** (removes notes and all associated cards, substitute actual IDs):
```bash
python3 .claude/anki.py '{"action": "deleteNotes", "params": {"notes": [<note_ids>]}}'
```

## Step 4 — Report

```
Deleted N card(s):
  ✓ [front snippet] — removed from Anki
```
