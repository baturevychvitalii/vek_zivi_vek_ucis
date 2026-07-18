---
format: 0
requires:
  - anki
---

# deck — SRS card-bearing base node

A bare DAFNE node: no memory, therefore not a grove. Also a root node —
no `parents/` directory; termination is expressed by absence. Parent
enumeration and URLs are the interpreter's job (`readdir(parents/)` +
`.gitmodules`), never manifest data.

Card-generation conventions shared by every deck-bearing node: input
syntax, card design rules, tagging skeleton, output format, cloze
mechanics.

| File | What |
|---|---|
| `./deck-defaults.md` | Core card generation contract |
| `./cloze-deletion.md` | Cloze syntax and when-not-to-cloze rules |

Consumers include from here explicitly — there is no single forced entry
point. (`language` includes both files; `instruments` includes only
`deck-defaults.md`.)
