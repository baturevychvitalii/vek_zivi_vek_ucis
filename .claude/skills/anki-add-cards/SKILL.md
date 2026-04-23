---
name: anki-add-cards
description: Generate Anki cards for a deck and push to AnkiConnect
disable-model-invocation: true
---

Generate Anki cards for any deck and push them to AnkiConnect.

Card generation runs in an isolated subprocess with only compiled context — no CLAUDE.md, no memory, no rules.

## Step 1 — Resolve Deck

Parse `$ARGUMENTS`: the first word is the deck name, everything after is the card input.

If no deck name given: list subdirectories of `decks/` and ask the user which deck to use.

Read `decks/<deck>/context.md` (leaf file only — do NOT walk the inheritance chain). Extract:
- **Deck Config** block: `deckName`, `basicModel`, `clozeModel`

If the directory `decks/<deck>/` does not exist: report "Deck '<deck>' not found. Available decks: [list]" and stop.

## Step 2 — Get Input

If input (the part after the deck name) is non-empty, use it as the card input.
If input is already in a form of generated cards - jump to ## Preview step
If empty, ask: "What would you like to turn into cards?"

## Step 3 — Generate Cards (isolated subagent)

The compiled context file exists at `decks/<...>/<deck>/compiled.md`.

Read that file. Then read `/tmp/card-generation-context.md` (ignore its current contents — this satisfies the Write tool's read-first constraint). Then write the compiled context to `/tmp/card-generation-context.md` using the Write tool.

Invoke the `/generate-cards` skill with the card input as its arguments.

The skill runs in a forked subagent with no conversation history. It reads `/tmp/card-generation-context.md` as its system context and receives the card input as its prompt.

Capture the skill output — this is the generated card output.

If the skill fails or returns empty output: report the error and stop.

## Step 4 — Preview

Display the generated cards to the user. Use the same numbered format as the compiled context specifies.

## Step 5 — User Confirmation

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

Pass the JSON payload as a single-quoted string argument directly:

```bash
python3 .claude/scripts/anki.py '<json payload>'
```

Parse the output: `result["result"]` is a list — non-null = added, null = duplicate/skipped.

If connection fails: warn the user — cards were not added to Anki.
Final confirm: "Added X cloze card(s) and Y basic card(s) — pushed to Anki."
