---
name: anki-process-red-edit
description: Find RED-flagged cards and apply edit instructions
disable-model-invocation: true
---

Find all RED-flagged cards in a deck, apply the `[instruction]` written in any field to that very field, then flip the flag to GREEN.

**Usage:** `/anki-process-red-edit <deck>` — e.g. `/anki-process-red-edit spanish`

## Step 0 — Load Deck Context

Read `decks/<deck>/compiled.md`. Keep the deck-specific editing guidelines in context.

## Step 1 — Find Flagged Cards

Call `mcp__anki__get_flagged_notes` with `deck=<deck>` and `flag="red"`.

If empty: report "No RED-flagged cards found in <deck>." and stop.

## Step 2 — Extract Instructions

For each card, scan every field in `card["fields"]` for text matching `[...]`. That is the instruction. Strip it (including brackets) from whichever field it appears in.

Skip cards with no instruction — include in final report as "no instruction found — flag left as RED."

## Step 3 — Edit Cards

Write `decks/<deck>/compiled.md` contents to `/tmp/card-edit-context.md`.

Invoke `/edit-card` once with all cards as one batch. Per-card block format:

```
[note_id: <note_id>] <model_name> card
<field_name>: <value>
<field_name>: <value>
... (all fields, using their real Anki names)
Tags: <tags>
Instruction: <instruction>

```

Parse output by `note_id` anchor (not position). Display all proposed edits numbered.

## Step 4 — User Confirmation

Ask: **"Apply these N change(s)? [yes / no]"** Respect per-card skips.

## Step 5 — Apply Changes

For each confirmed card:
1. Call `mcp__anki__update_note_fields` with `note_id` and a dict of only the fields that changed.
2. Call `mcp__anki__set_card_flag` with `card_id` and `flag="green"`.

## Step 6 — Report

```
Processed N card(s):
  ✓ [first-field snippet] — [one-line summary of change]
  ⚠ [first-field snippet] — skipped (no instruction / user skipped)
```
