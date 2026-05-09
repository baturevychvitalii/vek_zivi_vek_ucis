### User Input Syntax

- `{word}` — explicit cloze deletion. Always generate a cloze card for this word. If no cue is provided, generate one. 
- `{word::cue}` — explicit cloze with user-provided cue. Use the cue verbatim.

## Tagging

```
level::A1 / A2 / B1 / B2 / C1 / C2 
freq::top500 / top1000 / top2000 / top5000 / less_common

grammar::<construct name>
grammar::irregular_verbs / exceptions

vocab::<vocab category name>
vocab::expression::<expression>
vocab::idiom::<idiom>
```

### Output Format

- Cloze deletion **always** belongs to the front of the card
    + Single cloze: `{{c1::word}}`
    + Multiple: `{{c1::word1}} {{c2::word2}}`
    + With cue: `{{c1::word::cue}}`


### Quality Check 
- Is cloze actually improving retention?
