Generate Anki cards for any deck and append them to the correct files.

## Step 1 — Resolve Deck

Parse `$ARGUMENTS`: the first word is the deck name, everything after is the card input.

If no deck name given: list subdirectories of `decks/` and ask the user which deck to use.

Read `decks/<deck>/context.md`. Extract:
- **Deck Config** block: `deckName`, `basicFile`, `clozeFile`, `basicModel`, `clozeModel`
- **Card Generation Rules** section: the full generation instructions for this deck

If the directory `decks/<deck>/` does not exist: report "Deck '<deck>' not found. Available decks: [list]" and stop.

## Step 2 — Get Input

If input (the part after the deck name) is non-empty, use it as the card input.
If empty, ask: "What would you like to turn into cards?"

## Step 3 — Generate Cards

Apply the Card Generation Rules from `context.md` exactly as written for this deck.

Format output in two code blocks (omit a block if no cards of that type were generated):

```
[cloze cards — one per line: Front | Back | tags]
```

```
[production/pattern/aesthetic cards — one per line: Front | Back | tags]
```

Rules:
- `|` separates columns
- `<br>` for line breaks within a cell
- No commentary inside code blocks
- **For display only:** prefix each line with a number (`1.`, `2.`, etc.) so the user can read them easily. Strip the numbers before appending to files.

## Step 4 — Append to Files

After the user confirms the cards look good:

- Strip display line numbers from each line
- Append cloze cards to `clozeFile`
- Append production/pattern/aesthetic cards to `basicFile`

Do NOT overwrite. Always append.

## Step 5 — Push to AnkiConnect

Parse the confirmed cards (strip display line numbers). Split each line on ` | ` → col1 (front/text), col2 (back), col3 (tags, space-separated).

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

If connection fails: warn and continue — files are already updated, nothing is lost.
Final confirm: "Added X cloze card(s) and Y basic card(s) — pushed to Anki."
