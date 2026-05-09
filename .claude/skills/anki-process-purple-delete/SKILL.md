---
name: anki-process-purple-delete
description: Find and delete all PURPLE-flagged cards in Anki
disable-model-invocation: true
---

Find all PURPLE-flagged cards in Anki, show them for confirmation, then permanently delete them from Anki.

## Step 1 — Find PURPLE-flagged Cards

Call `mcp__anki__find_flagged_cards` with `flag="purple"` → `card_ids`.

If no card IDs: report "No PURPLE-flagged cards found." and stop.

Call `mcp__anki__cards_info` with `card_ids` → list of card objects.

Extract `note_ids` as the deduplicated list of `card["note"]` values.

Call `mcp__anki__notes_info` with `note_ids` → list of note objects. Build a `notes` dict keyed by `noteId`.

## Step 2 — Show Deletion List
- Display what is to be deleted

```
About to permanently delete N card(s):
This cannot be undone. Confirm? [yes / no]
```

## Step 3 — Delete

On confirmation, call `mcp__anki__delete_notes` with `note_ids`.
