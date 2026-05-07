---
name: anki-process-red-edit
description: Find RED-flagged cards and apply edit instructions
disable-model-invocation: true
---

Find all RED-flagged cards in a specific Anki deck, read the `[instruction]` written on the back, apply the requested change in-place in Anki, then flip the flag to GREEN.

**Usage:** `/anki-process-red-edit <deck>` — e.g. `/anki-process-red-edit spanish` or `/anki-process-red-edit english`

## Step 0 — Load Deck Context

The argument `<deck>` is a folder name under `decks/` (e.g. `spanish`, `english`).

Read `decks/<deck>/context.md` in full. From the Deck Config block extract:
- `deckName` (the Anki deck name, e.g. "Español")

The rest of the file contains deck-specific editing guidelines — keep them in context; they inform how to interpret and apply card instructions in Step 3.

## Step 1 — Find Flagged Cards

Call `mcp__anki__find_flagged_cards` with `flag="red"` → `card_ids`.

If no card IDs: report "No RED-flagged cards found." and stop.

Call `mcp__anki__cards_info` with `card_ids` → list of card objects.

Filter to only cards where `card["deckName"] == deckName` (from Step 0). If none remain after filtering: report "No RED-flagged cards found in <deck>." and stop.

Extract `note_ids` as the deduplicated list of `card["note"]` values.

Call `mcp__anki__notes_info` with `note_ids` → list of note objects. Build a `notes` dict keyed by `noteId`.

## Step 2 — Extract Instructions

For each card, collect:
- `card_id`: the card's ID (needed for flag change)
- `note_id`: `card["note"]`
- `deck`: `card["deckName"]`
- `model`: `card["modelName"]`
- `front`: `note["fields"]["Front"]["value"]` for Basic, or `note["fields"]["Text"]["value"]` for Cloze
- `back`: `note["fields"]["Back"]["value"]` for Basic, or `note["fields"]["Back Extra"]["value"]` for Cloze
- `instruction`: text inside `[...]` found anywhere in the back field. Strip it (including the brackets) from the back.

If a card has no `[...]` in the back: skip it, note it in the final report as "no instruction found — flag left as RED."

## Step 3 — Edit Cards (isolated subagent)

The compiled context file lives at `decks/<deck>/compiled.md` (same path convention as `anki-add-cards`).

Read that file, then write its contents to `/tmp/card-edit-context.md` using the Write tool.

Invoke the `/edit-card` skill **once** with all cards concatenated as arguments. Format each card block as:

```
[note_id: <note_id>] <model> card
Front: <front>
Back: <back> (instruction already stripped)
Tags: <tags>
Instruction: <instruction>

```

The skill returns one edited card per block, each prefixed with `[note_id: <id>]`. Parse the output by matching `note_id` anchors back to the original cards — do not rely on position.

Display all proposed edits numbered (same output format as the compiled context specifies).

If the instruction mentions tags only (e.g., "wrong tag") → note that tag changes are not handled here and leave for manual fix; still flip flag to GREEN.

## Step 4 - User Confirmation

Ask the user: **"Apply these N change(s)? [yes / no]"**

If the user says no or wants to skip individual cards, respect that.

## Step 5 — Apply Changes

For each confirmed card, in order:

1. Call `mcp__anki__update_note_fields` with the note's `note_id` and updated fields:
   - Basic card: `{"Front": "<new_front>", "Back": "<new_back>"}`
   - Cloze card: `{"Text": "<new_text>", "Back Extra": "<new_back_extra>"}`

2. Call `mcp__anki__set_card_flag` with the card's `card_id` and `flag="green"`.

## Step 5 — Report

```
Processed N card(s):
  ✓ [front snippet] — [one-line summary of change]
  ✓ ...
  ⚠ [front snippet] — skipped (no instruction / user skipped)
```
