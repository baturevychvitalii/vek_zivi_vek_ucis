# English Deck — Workspace Context

## What This Workspace Is

Classical and literary English vocabulary deck. Focus is on lexical depth, IPA pronunciation, and aesthetic recitation of notable passages.

## Files

| File | Purpose |
|---|---|
| `basic.csv` | Aesthetic cards (append here) |
| `cloze.csv` | Vocabulary cloze cards (append here) |
| `english_gemini_prompt.txt` | Legacy Gemini prompt — kept as reference, no longer the active workflow |
| `todo` | Open issues (now resolved — see skill for authoritative rules) |

## How to Add Cards

Use the `/add-english` skill. It handles card generation, formatting, tagging, and appending to the correct file.

```
/add-english
```

Then provide your input in the format: `Text | Book Title | Chapter/Location`

Or pass input directly:

```
/add-english The {firmament} stretched above | Paradise Lost | Book I
```

## Input Format

```
Text | Book Title | Chapter/Location
```

- Wrap vocabulary targets in `{curly brackets}` → generates cloze card
- No brackets → generates aesthetic card
- Multiple `{bracketed}` words on the same line → one card with sequential clozes

## Key Rules (Summary)

- **Cloze cards:** front has the passage with `{{c1::}}` clozes; back has Webster definition + British/Oxford IPA + reference line
- **Aesthetic cards:** front is `[Book Title]: first 3–5 words...`; back is full passage + reference line
- **Tags:** always `level::*` + `cardtype::*` + `book::*` + `period::*`; add `utility::*` and misc tags as appropriate
- **Levels:** C1 or C2 only (this is classical/literary material)

See `/add-english` skill for full rules.
