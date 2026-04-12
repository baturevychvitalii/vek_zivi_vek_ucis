# Spanish Deck — Workspace Context

## What This Workspace Is

Rioplatense Spanish (Argentine dialect) Anki card deck. Focus is on production-oriented active recall — the learner should be able to speak, not just recognize.

## Files

| File | Purpose |
|---|---|
| `basic_spanish_gpt.txt` | Production + Pattern cards (append here) |
| `cloze_spanish_gpt.txt` | Cloze cards (append here) |
| `spanish_daily_prompt.txt` | Legacy GPT prompt — kept as reference, no longer the active workflow |

## How to Add Cards

Use the `/add-spanish` skill. It handles card generation, formatting, tagging, and appending to the correct file.

```
/add-spanish
```

Then provide your input (phrases, sentences, expressions — one per line).

Or pass input directly:

```
/add-spanish extrañar a alguien
```

## Key Rules (Summary)

- **Dialect:** Rioplatense / Argentine voseo by default (`vos hablás`, `vos tenés`)
- **Card types:** production (EN→ES), pattern (grammar formula), cloze (only when it genuinely aids encoding)
- **No recognition cards** (ES→EN) — intentionally excluded
- **Tags:** always `level::*` + `cardtype::*`, then grammar or vocab as relevant; 3–6 tags total
- **Cloze triggers:** irregular conjugations, pronoun placement, prepositions, tense contrasts, dialect forms, contractions, superlatives, or explicit `{{word}}` in input

See `/add-spanish` skill for full rules.
