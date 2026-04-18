# Deck Defaults

Shared rules inherited by all decks.
Apply all rules below strictly.
Deck-specific `context.md` files extend, or, if conflicting - override these.

## Models for communicating with Anki

```
basicModel: "Basic"
clozeModel: "Cloze"
```

## Card Generation Rules (shared)

### Input Rules
- One card input per line break — multiple sentences on one line = one input
- Generate as many cards as the input warrants; never fewer than implied; no filler cards

### User Input Syntax

- `{word}` — explicit cloze trigger. Always generate a cloze card for this word. If no cue is provided, generate one (e.g., `{{c1::word::grammatical role or short hint}}`).
- `{word::cue}` — explicit cloze with user-provided cue. Use the cue verbatim.
- `| extra text` — append everything after `|` to the back of the card with `<br>`.
- `[instruction]` — parse and process the instruction when preparing a card. Also used in red-flag card processing.

### Card Design Rules
- One learning objective per card
- No redundant paraphrase cards

### Tagging (shared)

Always include `cardtype::*`. 3–6 tags total. Additional mandatory tags may be defined per deck or domain.

```
cardtype::<type>     (mandatory — types defined per deck)
```

### Output Format

Cards are previewed before conversion to AnkiConnect payloads:
- `<br>` for line breaks within a cell
- Front:
    * Cloze deletion **always** belongs to the front of the card
        + Single cloze: `{{c1::word}}`
        + Multiple: `{{c1::word1}} {{c2::word2}}`
        + With cue: `{{c1::word::cue}}`


```
Front:
Back:
<tag1 tag2 tag3>
```
