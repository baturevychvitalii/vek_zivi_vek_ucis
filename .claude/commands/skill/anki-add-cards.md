Generate Anki cards for any deck and push them to AnkiConnect.

## Step 1 — Resolve Deck

Parse `$ARGUMENTS`: the first word is the deck name, everything after is the card input.

If no deck name given: list subdirectories of `decks/` and ask the user which deck to use.

Read `decks/<deck>/context.md`. Extract:
- **Deck Config** block: `deckName`, `basicModel`, `clozeModel`
- **Card Generation Rules** section: the full generation instructions for this deck

If the directory `decks/<deck>/` does not exist: report "Deck '<deck>' not found. Available decks: [list]" and stop.

## Step 2 — Get Input

If input (the part after the deck name) is non-empty, use it as the card input.
If input is already in a form of generated cards - jump to ## Preview step
If empty, ask: "What would you like to turn into cards?"

## Step 3 — Generate Cards

Apply the Card Generation Rules from deck's `context.md` exactly as written for this deck.

## Step 4 - Preview
- Display output according to deck's `context.md`.

## Step 5 - User Confirmation

Ask the user: **"Apply these N change(s)? [yes / no]"**

If the user says no or wants to skip individual cards, respect that.

## Step 6 — Push to AnkiConnect

After the user confirms the cards look good, strip display line numbers and use the parsed cards (col1, col2, col3 split on ` | `).

Build the AnkiConnect payload using values from Deck Config:
- Cloze cards → `modelName: <clozeModel>`, fields: `{"Text": col1, "Back Extra": col2}`, `deckName: <deckName>`
- Basic cards → `modelName: <basicModel>`, fields: `{"Front": col1, "Back": col2}`, `deckName: <deckName>`

```json
{
  "action": "addNotes",
  "params": {
    "notes": [
      {
        "deckName": "<deckName>",
        "modelName": "<clozeModel or basicModel>",
        "fields": {"Text": "<col1>", "Back Extra": "<col2>"},
        "tags": ["<tag1>", "<tag2>"]
      }
    ]
  }
}
```

Write this JSON to `/tmp/anki_payload.json` using the Write tool, then run:

```bash
python3 .claude/anki.py /tmp/anki_payload.json
```

Parse the output: `result["result"]` is a list — non-null = added, null = duplicate/skipped.

If connection fails: warn the user — cards were not added to Anki.
Final confirm: "Added X cloze card(s) and Y basic card(s) — pushed to Anki."
