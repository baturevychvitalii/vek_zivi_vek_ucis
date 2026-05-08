# add_notes Reference

## Note Dict Schema

```json
{
  "deckName": "Spanish",
  "modelName": "Basic",
  "fields": {
    "Front": "¿Cómo te llamas?",
    "Back": "What is your name?"
  },
  "tags": ["greetings", "ch1"]
}
```

All four keys are required. `tags` may be an empty list `[]`.

## Field Values by Model Type

| Model | Required fields | Notes |
|---|---|---|
| `Basic` | `Front`, `Back` | Plain text or HTML |
| `Basic (and reversed card)` | `Front`, `Back` | Generates two cards automatically |
| `Cloze` | `Text` | Must contain at least one `{{c1::…}}` marker |
| Custom | whatever the model defines | Use `model_field_names(model_name)` to check |

## Cloze Syntax in Field Values

| Pattern | Effect |
|---|---|
| `{{c1::word}}` | Single deletion |
| `{{c1::first}} and {{c2::second}}` | Two separate cards |
| `He lived from {{c1::1856}} to {{c1::1943}}` | Both blanked together on one card |

The cloze model must be used — cloze markers in a Basic note are rendered as literal text.

## Media in Field Values

| Syntax | Effect |
|---|---|
| `[sound:file.mp3]` | Audio playback — file must exist in Anki media collection |
| `<img src="file.jpg">` | Image — file must exist in Anki media collection |

Use `store_media_file` to upload a file before referencing it here.

## Return Value

Returns a list of integers in the same order as input.
A `null` at position _i_ means note _i_ was a duplicate and was skipped — the existing note is unchanged.

Use `can_add_notes` with the same list to dry-run duplicate detection before committing.

## Tags Conventions

- Use lowercase, dot-separated hierarchy: `grammar.subjunctive`, `vocab.food`
- Deck name is not a tag — `deckName` controls placement
- Tags are additive; `update_note_tags` / `add_tags` can amend later without re-adding the note
