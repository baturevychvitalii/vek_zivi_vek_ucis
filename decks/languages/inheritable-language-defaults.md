# Language Deck Extension

Shared rules for all language decks.

## Models for communicating with Anki

```
basicModel: "Basic"
clozeModel: "Cloze"
```

### User Input Syntax (extension for language cards)

- `{word}` — explicit cloze trigger. Always generate a cloze card for this word. If no cue is provided, generate one (e.g., `{{c1::word::grammatical role or short hint}}`).
- `{word::cue}` — explicit cloze with user-provided cue. Use the cue verbatim.

## Tagging (language-shared)

Always include `level::*` in addition to `cardtype::*`.

```
level::A1 / A2 / B1 / B2 / C1 / C2     (mandatory for all language decks)
```

### Output Format (language-shared)

- Cloze deletion **always** belongs to the front of the card
    + Single cloze: `{{c1::word}}`
    + Multiple: `{{c1::word1}} {{c2::word2}}`
    + With cue: `{{c1::word::cue}}`


### Quality Check 
- Is cloze actually improving retention?
