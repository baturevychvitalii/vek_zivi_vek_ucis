---
format: 0
requires: []
banks:
  - name: spanish-reading
    bank: ./reading-log
    graduate: false
    patterns:
      - "reading-log/context\\.md"
---

# spanish — Rioplatense Spanish grove

A **grove**: a DAFNE node carrying memory (the banks above). The
grove-ness is inferred structurally from the bank declaration — there is
no `type:` field. One parent: `parents/language`.

Rioplatense Spanish (Argentine/River Plate dialect) knowledge enclave.
Anki card specification and overall progression. Literature search and
analysis.

| File | What |
|---|---|
| `./rioplatense-anki.md` | Main deck context — compiled via context-compiler before card generation |
| `./focus_area.md` | Rioplatense dialect criteria (voseo, Argentine vocabulary) |
| `./reading-log/` | mem-bank: reading session history |
| `./deck_quality_bootstrapping/` | Deck quality & efficiency analysis snapshots |
