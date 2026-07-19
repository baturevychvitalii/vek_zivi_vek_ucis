### Input Rules
- One card input per line break — **multiple sentences on one line = one input**

### User Input Syntax - very strict

- `$ text` — append everything after `$` to the back of the card in addition to what you've generated.
- `[instruction]` — process and apply the instruction to this input line **before** preparing a card.
- `"quoted text"` - don't modify it, keep as is and put it on the front.
- `front | back` - Take front and back 1:1. **don't change anything**. You might add some details on the **back**, though.

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

## Card Type

Single type: **visual identification**.

**Front:** Image of the instrument — `<img src="<filename>">` where `<filename>` is a file stored in Anki's media collection.

**Back:**
- Instrument name in bold: `<b>Clarinet</b>`
- British IPA: `/ˌklærɪˈnɛt/`
- 2–4 sentence Wikipedia summary: family, origin, construction, notable use or sound character

## Adding Cards

When adding an instrument card:

1. **Find a clean image** — Wikipedia Commons is the preferred source (freely licensed, high quality). Pick a photo on white/neutral background where possible.
2. **Store the image in Anki media** via anki MCP:
   ```json
   {"action": "storeMediaFile", "params": {"filename": "<instrument>.jpg", "url": "<image_url>"}}
   ```
3. **Draft the back** from Wikipedia: name in bold, British IPA, 2–4 sentence summary.
4. **Add the note** using the Basic model with:
   - `Front`: `<img src="<instrument>.jpg">`
   - `Back`: `<b>Name</b> /IPA/<br><br>Summary text.`

## Tagging

```
cardtype::identification          (mandatory — only one card type in this deck)

family::woodwind / brass / string / percussion / keyboard / plucked / voice
origin::european / asian / african / latin_american / middle_eastern / universal
era::ancient / medieval / baroque / classical / modern
```

3–5 tags per card. `cardtype::identification` and `family::*` are mandatory.
