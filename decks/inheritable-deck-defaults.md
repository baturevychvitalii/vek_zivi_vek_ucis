### Input Rules
- One card input per line break — **multiple sentences on one line = one input**

### User Input Syntax

- `| extra text` — append everything after `|` to the back of the card in addition to what you've generated.
- `[instruction]` — process and apply the instruction to this input line **before** preparing a card.
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

- If binary file on the front — just give a brief description
- Choose the note type that best fits the card. Use an existing type from the Available Note Types list when one fits. If none fits well, propose a new name and field list.

```
[model: <ModelName>] card
<FieldName1>: <value1>
<FieldName2>: <value2>
.
<FieldNameN>: <valueN>
Tags: <tag1> <tag2>...<tagN>
```

**For display only**
Cards are previewed before conversion to Anki payloads and getting user confirmation.
Prefix each suggested card or card change with a number (`1.`, `2.`, etc.).
Strip numbers before processing.
