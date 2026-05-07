---
name: anki-process-purple-delete
description: Find and delete all PURPLE-flagged cards in Anki
disable-model-invocation: true
---

Find all PURPLE-flagged cards in Anki, show them for confirmation, then permanently delete them from Anki.

## Step 0 — Build Deck Map

Before doing anything else, scan `decks/` subdirectories and read `context.md` from each one.
For each deck extract the Deck Config block:
- `deckName` (the Anki deck name, e.g. "Español")

Build a lookup table of known `deckName` values. This is used for display and to identify which deck a card belongs to.

## Step 1 — Find PURPLE-flagged Cards

Call `mcp__anki__find_flagged_cards` with `flag="purple"` → `card_ids`.

If no card IDs: report "No PURPLE-flagged cards found." and stop.

Call `mcp__anki__cards_info` with `card_ids` → list of card objects.

Extract `note_ids` as the deduplicated list of `card["note"]` values.

Call `mcp__anki__notes_info` with `note_ids` → list of note objects. Build a `notes` dict keyed by `noteId`.

## Step 2 — Show Deletion List
- Display output according to deck's `context.md`.

```
About to permanently delete N card(s):
This cannot be undone. Confirm? [yes / no]
```

## Step 3 — Delete

On confirmation, call `mcp__anki__delete_notes` with `note_ids`.

## Step 4 — Report

```
Deleted N card(s):
  ✓ [front snippet] — removed from Anki
```
