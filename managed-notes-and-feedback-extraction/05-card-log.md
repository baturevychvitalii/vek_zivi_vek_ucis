# 05 — Card log field (was "Task B")

*Depends on: 01 (the `log` field is part of the managed contract). Analysis-first; do not rush to
implementation.*

## Goal

An append-only, hidden per-card `log` recording lifecycle events — so you can later assess
progress, bootstrap/reduce the deck as your knowledge or tooling improves, and roll changes back
without a backup.

## Why native Anki isn't enough

Anki natively stores the **review log (revlog)** — timing/ease/interval per review — and a per-note
`mod` timestamp. It has **no field-level edit history and no record of what a card was generated
from.** So the instinct is correct: native history does not support "what changed field-by-field"
or "which source produced this card."

## Events to log

- `created <ts> | source: <deck spec / input string>` — written by `anki-add-cards`.
- `edited <ts> | <feedback> | <field>: <before>→<after>` — written by red-edit (03).

Format: one parseable line per event (human-readable + machine-reversible). Hidden — `log` is not
referenced in card templates, so it never renders.

## The coupling decision — LOCKED (01)

- `Production` is Spanish-only → `log` is low-risk.
- `Cloze` is a global Anki model → **option 2 chosen**: add `log` globally. Empty on unrelated
  notes; trades purity for simplicity. Both fields are already being added by bootstrap (01).

- **Unify the write-path with 03/add-cards:** both edit and creation events append to the same
  `log` via one shared helper — don't add a separate logging mechanism.

## Done when (future)

- Managed models carry a hidden `log`; creation and edit events append consistently; a documented
  way to read/parse the log for retrospection exists.
