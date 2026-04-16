# Language Deck Defaults

Shared rules for all language decks. Extends `decks/context.md`.

## Models

```
clozeModel: "Cloze"
```

## Cloze Syntax

- Single cloze: `{{c1::word}}`
- Multiple: `{{c1::word1}} {{c2::word2}}`
- With cue: `{{c1::word::cue}}`

## Tagging (language-shared)

Always include `level::*` in addition to `cardtype::*`.

```
level::A1 / A2 / B1 / B2 / C1 / C2     (mandatory for all language decks)
```
