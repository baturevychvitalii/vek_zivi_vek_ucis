Find all PURPLE-flagged cards in Anki, show them for confirmation, then permanently delete them from Anki and from the source files.

## Step 1 — Find PURPLE-flagged Cards

```python
import json, urllib.request

def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request("http://localhost:8765", data=payload, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

card_ids = anki("findCards", query="flag:7")["result"]
```

If no cards found: report "No PURPLE-flagged cards found." and stop.

Fetch details:

```python
cards = anki("cardsInfo", cards=card_ids)["result"]
note_ids = list({c["note"] for c in cards})
notes_list = anki("notesInfo", notes=note_ids)["result"]
notes = {n["noteId"]: n for n in notes_list}
```

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

**Delete from Anki** (removes notes and all associated cards):
```python
result = anki("deleteNotes", notes=note_ids)
```

**Remove from source files** — for each card, find the line where col1 matches the front/text field (split on ` | `) and delete that line. Do not leave blank lines.

File mapping:
- "Español" + "Basic" → `spanish/basic_spanish_gpt.txt`
- "Español" + "Cloze" → `spanish/cloze_spanish_gpt.txt`
- "English" + "Basic" → `english/basic.csv`
- "English" + "Cloze" → `english/cloze.csv`

Use Python to rewrite each affected file without the deleted lines:
```python
with open(filepath, "r") as f:
    lines = f.readlines()
lines = [l for l in lines if not l.startswith(front_to_delete + " |")]
with open(filepath, "w") as f:
    f.writelines(lines)
```

If a card's line is not found in the source file: still delete from Anki, but warn "not found in source file."

## Step 4 — Report

```
Deleted N card(s):
  ✓ [front snippet] — removed from Anki and [filename]
  ⚠ [front snippet] — removed from Anki, not found in source file
```
