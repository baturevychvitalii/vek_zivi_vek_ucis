# Instruments Deck

## Deck Config

```
deckName: "Instruments"
```

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
2. **Store the image in Anki media** via AnkiConnect `storeMediaFile`:
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
