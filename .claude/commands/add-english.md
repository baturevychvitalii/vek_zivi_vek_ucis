Generate English Anki cards from classical/literary passages and append them to the correct deck files.

## Step 1 — Get Input

If `$ARGUMENTS` is non-empty, treat it as the card input.
If `$ARGUMENTS` is empty, ask the user: "Paste your passage(s) in the format: Text | Book Title | Chapter/Location"

## Step 2 — Generate Cards

You are an elite English Philologist and Anki system architect. Focus on lexical precision and aesthetic recitation of classical literature.

### Input Format
```
Text | Book Title | Chapter/Location
```

- Wrap vocabulary targets in `{curly brackets}` → triggers a cloze card
- No brackets → triggers an aesthetic card
- Process one input per line

### Cloze Logic
- MULTI-CLOZE: Multiple `{bracketed}` words on the same line → ONE card with sequential clozes `{{c1::word1}}`, `{{c2::word2}}`, etc.
- LINE BREAK: Each new line = separate card

### Card Types

**Cloze Cards** (only for `{bracketed}` words)
- Front: full passage with `{{c1::word}}` cloze syntax replacing the bracketed words
- Back: for each clozed word — Webster's Definition (chronological depth preferred) + British/Oxford IPA pronunciation
- End of back: `<br><br>Ref: [Book Title], [Chapter/Canto], [Page/Line]`

**Aesthetic Cards** (only when NO brackets used)
- Front: `[Book Title]: [first 3–5 words of passage]...`
- Back: full passage + `<br><br>Ref: [Book Title], [Chapter/Canto], [Page/Line]`

### Tagging (strict)

Always include `level::*`, `cardtype::*`, `book::*`, `period::*`. 3–6 tags total.

```
level::C1 / C2                                           (mandatory — this is classical material)
cardtype::cloze / aesthetic                              (mandatory)
book::<title>                                            (mandatory)
period::classical / renaissance / victorian / modern    (mandatory)
utility::high / niche
difficulty::tricky_ipa
register::poetic / register::philosophical
```

### Output Format

Produce two code blocks (omit a block if no cards of that type were generated):

```
[cloze cards — one per line: Front | Back | tags]
```

```
[aesthetic cards — one per line: Front | Back | tags]
```

Rules:
- `|` separates columns
- `<br>` for line breaks within a cell
- `<br><br>` before the Ref line
- No commentary inside code blocks

## Step 3 — Append to Files

After showing the cards to the user and confirming they look good:

- Append cloze cards to `english/cloze.csv`
- Append aesthetic cards to `english/basic.csv`

Do NOT overwrite. Always append.

## Step 4 — Push to AnkiConnect

After appending to files, push the same cards to Anki.

Parse the confirmed cards. Split each line on ` | ` → col1 (front/text), col2 (back), col3 (tags, space-separated).

Build the AnkiConnect payload:
- Cloze cards → `modelName: "Cloze"`, fields: `{"Text": col1, "Back Extra": col2}`, `deckName: "English"`
- Aesthetic cards → `modelName: "Basic"`, fields: `{"Front": col1, "Back": col2}`, `deckName: "English"`

```json
{
  "action": "addNotes",
  "params": {
    "notes": [
      {
        "deckName": "English",
        "modelName": "Cloze",
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
Final confirm: "Added X cloze card(s) and Y aesthetic card(s) — pushed to Anki."
