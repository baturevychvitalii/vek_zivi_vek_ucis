## Deck Config

```
(deck-specific config only — no model defaults)
```

### Input Rules
- One card input per line break — **multiple sentences on one line = one input**

### User Input Syntax

- `| extra text` — append everything after `|` to the back of the card with `<br>` in addition to the back that you've generated.
- `[instruction]` — parse and process the instruction when preparing a card. Also used in red-flag card processing.
- `"quoted text"` - don't modify it, keep as is and put it on the front.

### Card Design Rules
- Generate as many cards as the input warrants; never fewer than implied; no filler cards

### Tagging

- Always include `cardtype::*`.
- Are tags minimal but sufficient? 3–6 tags total.

```
cardtype::<type>     (mandatory — types defined per deck)
```

### Output Format

- `<br>` for line breaks within a field value
- If binary file on the front — just give a brief description
- Choose the note type that best fits the card. Use an existing type from the Available Note Types list when one fits. If none fits well, propose a new name and field list.

```
[model: <ModelName>] card
<FieldName>: <value>
<FieldName>: <value>
Tags: <tag1> <tag2> <tag3>
```

**For display only**
Cards are previewed before conversion to AnkiConnect payloads and getting user confirmation.
Prefix each suggested card or card change with a number (`1.`, `2.`, etc.).
Strip numbers before processing.
