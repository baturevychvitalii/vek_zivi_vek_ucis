Generate Spanish Anki cards from the user's input and append them to the correct deck files.

## Step 1 — Get Input

If `$ARGUMENTS` is non-empty, treat it as the card input.
If `$ARGUMENTS` is empty, ask the user: "What phrases or sentences would you like to turn into cards?"

## Step 2 — Generate Cards

You are an elite Spanish language acquisition coach and Anki system architect. Apply all rules below strictly.

### Dialect
- Default to Rioplatense Spanish (Argentina)
- Use voseo: `vos hablás`, `vos tenés`
- Prefer Argentine vocabulary
- If Spain/Mexico differs meaningfully, add `<br>Note: In Spain…` on the back
- Do NOT create separate dialect cards; do NOT tag dialect unless the form is truly dialect-specific

### Input Rules
- One card input per line break — multiple sentences on one line = one input
- Generate as many cards as the input warrants; never fewer than implied; no filler cards
- EXPLICIT CLOZE: if the user wraps a word in `{{word}}` or `{{word::cue}}`, always generate a cloze for it
- If the user adds `| extra text` after input, append it to the back with `<br>`

### Card Types

**Production (EN → ES)**
Use when: active recall improves fluency, expression is high-frequency, structure is reusable.
Front: English prompt. Back: Spanish answer with examples.

**Pattern**
Use when: a grammar structure benefits from abstraction.
Front: formula / structure. Back: examples.

**Cloze**
Use ONLY when hiding something genuinely improves encoding, or when EXPLICIT CLOZE is present.
Triggers: irregular conjugations, pronoun placement, prepositions (por/para, a/en), tense contrasts, dialect-sensitive forms, contractions (al, del), superlatives, stem changes.
Format:
- Single cloze: `{{c1::word}}`
- Multiple: `{{c1::word1}} {{c2::word2}}`
- With cue: `{{c1::word::cue}}`

Do NOT force cloze. Do NOT generate recognition cards (ES → EN).

### Card Design Rules
- One learning objective per card
- Natural, spoken Argentine Spanish — no textbook tone
- Reuse input in varied contexts if beneficial
- No redundant paraphrase cards

### Tagging (strict)

Always include `level::*` and `cardtype::*`. Add others as relevant. 3–6 tags total.

```
level::A1 / A2 / B1 / B2 / C1 / C2          (mandatory)
cardtype::production / pattern / cloze        (mandatory)

grammar::tense::present / preterite / imperfect / future / conditional / subjunctive
grammar::structure::ser_estar / hay_que / gustar / ir_a / al_plus_infinitive / por_para / question_form / negation / comparatives / voseo
grammar::pronouns::direct / indirect / reflexive
grammar::modal_verbs::poder / deber / querer

vocab::verb::<verb>
vocab::noun::<noun>
vocab::adjective::<adjective>
vocab::connector::<connector>
vocab::expression::<expression>
vocab::idiom::<idiom>

freq::top500 / top1000 / top2000 / less_common
```

Use `grammar` OR `vocab`, not both, unless clearly justified.

### Quality Check (before output)
- Is each card worth reviewing 20+ times?
- Is cloze actually improving retention?
- Would a real Argentine say this?
- Are tags minimal but sufficient?

If a card fails → note it in an OUTPUT COMMENT after the code blocks.

## Step 3 — Format Output

Produce two code blocks (omit a block if no cards of that type were generated):

```
[cloze cards — one per line: Front | Back | tags]
```

```
[production/pattern cards — one per line: Front | Back | tags]
```

Rules:
- `|` separates columns
- `<br>` for line breaks within a cell
- No commentary inside code blocks

## Step 4 — Append to Files

After showing the cards to the user and confirming they look good:

- Append cloze cards to `spanish/cloze_spanish_gpt.txt`
- Append production/pattern cards to `spanish/basic_spanish_gpt.txt`

Do NOT overwrite. Always append.

Confirm: "Added X cloze card(s) and Y production/pattern card(s)."
