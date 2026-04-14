Find all RED-flagged cards in Anki, read the `[instruction]` written on the back, apply the requested change in-place, update the source file, then flip the flag to GREEN.

## Step 1 — Find Flagged Cards

Run each command and parse the JSON output printed to stdout.

Find RED-flagged cards (flag:1):
```bash
python3 .claude/anki.py '{"action": "findCards", "params": {"query": "flag:1"}}'
```
→ `result["result"]` is `card_ids` (list of integers).

If no card IDs: report "No RED-flagged cards found." and stop.

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

## Step 3 — Propose Changes

For each card with an instruction, interpret it and propose the edit. Show:

```
Card N — [front text, truncated to 70 chars if needed]
Deck: [deckName] | Type: [modelName]
Instruction: [extracted instruction]
→ Proposed change: [describe exactly what will be updated and show the new field value]
```

Apply instructions using judgment:
- "cloze too obvious / too easy" → make the hint more specific, or remove the hint entirely
- "cloze too hard / too cryptic" → add or improve the `::hint` part
- "wrong translation / wrong word" → correct it
- "bad example / update example" → replace with a better one
- "add example" → append a new example to the back
- Any other natural language instruction → interpret and apply

The `[...]` instruction text is always removed from the back in the updated version.

If the instruction mentions tags only (e.g., "wrong tag") → note that tag changes are not handled here and leave for manual fix; still flip flag to GREEN.

Ask the user: **"Apply these N change(s)? [yes / no]"**

If the user says no or wants to skip individual cards, respect that.

## Step 4 — Apply Changes

For each confirmed change:

**Update note fields in Anki** — build the payload, write to `/tmp/anki_note_update.json` using the Write tool, then run:

```bash
python3 .claude/anki.py /tmp/anki_note_update.json
```

Payload for Basic card:
```json
{"action": "updateNoteFields", "params": {"note": {"id": <note_id>, "fields": {"Front": "<new_front>", "Back": "<new_back>"}}}}
```

Payload for Cloze card:
```json
{"action": "updateNoteFields", "params": {"note": {"id": <note_id>, "fields": {"Text": "<new_text>", "Back Extra": "<new_back_extra>"}}}}
```

**Flip flag RED → GREEN** (substitute actual card_id):
```bash
python3 .claude/anki.py '{"action": "setSpecificValueOfCard", "params": {"card": <card_id>, "keys": ["flags"], "newValues": [3]}}'
```

**Update source file** — find the line where col1 matches the original front/text value (split on ` | `), replace the entire line with the updated card in `Front | Back | tags` format. Tags come from the existing note tags joined by spaces.

File mapping:
- "Español" + "Basic" → `spanish/basic_spanish_gpt.txt`
- "Español" + "Cloze" → `spanish/cloze_spanish_gpt.txt`
- "English" + "Basic" → `english/basic.csv`
- "English" + "Cloze" → `english/cloze.csv`

If no matching line is found in the file: append the updated card and warn "line not found in source file — appended."

## Step 5 — Report

```
Processed N card(s):
  ✓ [front snippet] — [one-line summary of change]
  ✓ ...
  ⚠ [front snippet] — skipped (no instruction / user skipped)
```
