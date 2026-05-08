# Anki Template & CSS Reference

## Template Syntax

| Syntax | Effect |
|---|---|
| `{{FieldName}}` | Insert field value |
| `{{FrontSide}}` | Repeat the rendered front on the back |
| `{{#Field}}…{{/Field}}` | Show block only if field is non-empty |
| `{{^Field}}…{{/Field}}` | Show block only if field is empty |
| `{{cloze:Field}}` | Cloze deletion — front hides `{{c1::…}}`, back reveals |
| `{{type:Field}}` | Type-in-the-answer input box |

## Standard HTML Elements

| Element | Purpose |
|---|---|
| `<hr id=answer>` | The flip divider — Anki hides everything after this on the front |
| `[sound:file.mp3]` | Audio playback — place directly in any field value |
| `<img src="file.jpg">` | Image stored in Anki's media collection |

## CSS Conventions

| Selector | When it applies |
|---|---|
| `.card` | All cards — base styles go here |
| `.nightMode .card` | Dark mode override |
| `.cloze` | The hidden/revealed cloze span |
| `.nightMode .cloze` | Dark mode cloze override |
| `hr#answer` | The flip divider element — style with `border`, `width`, `margin` |

## Project Conventions

- Always include `.nightMode` rules — users review in dark mode
- Use `{{#Field}}…{{/Field}}` for optional fields so empty ones leave no gap
- Named CSS classes (`.primary`, `.notes-block`) over inline styles — easier to update via `update_model_styling`

## Multiple Card Templates

One note type can generate multiple cards — each template produces one card per note:

```json
{
  "Card 1": {"Front": "{{Word}}", "Back": "{{FrontSide}}<hr id=answer>{{Definition}}"},
  "Card 2": {"Front": "{{Definition}}", "Back": "{{FrontSide}}<hr id=answer>{{Word}}"}
}
```

Pass all templates in a single `update_model_templates` call.

## Cloze Notes

For `is_cloze=True` models, field values contain `{{c1::hidden}}` markers.
Multiple clozes: `{{c1::first}} and {{c2::second}}` — each becomes a separate card.
Same ordinal in one field: `He lived from {{c1::1856}} to {{c1::1943}}` — blanked together.

## JavaScript

Anki renders in a WebView — full browser JS is available:

```html
<div id="extra" style="display:none">Hidden detail</div>
<button onclick="document.getElementById('extra').style.display='block'">Reveal</button>
```

Use `document.addEventListener('DOMContentLoaded', fn)` for reliable initialization.
Audio, Canvas, fetch to localhost — all work.
