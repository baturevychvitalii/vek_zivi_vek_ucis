# 02 — Feedback extractor (deterministic anki-mcp tool)

*Depends on: 01 (field contract + managed-model set).*

## Goal

A deterministic anki-mcp tool that finds cards whose `user_feedback` is non-empty, emits a
structured JSON payload, and flags them RED for visual convenience — the single shared extraction
primitive for both red-edit (03) and refine (04). No LLM in this step (D3).

## Design

**New anki-mcp tool**, e.g. `extract_feedback(models | deck)`:
1. Find notes in the managed models (or a given deck) with non-empty `user_feedback`
   (`find_notes` + `notes_info`, or a query).
2. For each, build a record: `{note_id, card_id, model, fields, user_feedback, tags}`.
3. **Set the RED flag** on each matched card (`set_card_flag`) — visual only (D2); the trigger is
   the field, not the flag (D1).
4. Return the JSON list (and optionally write it next to the deck's `.compiled.md` if a path is
   given, so a later standalone refine can read it).

Deterministic and side-effecting only in the flag-setting sense; the payload is pure data for the
LLM steps to reason over.

## Done when

- anki-mcp exposes `extract_feedback(...)` returning the record schema above, committed upstream +
  pointer bumped.
- Running it on Spanish returns exactly the cards with non-empty `user_feedback` and RED-flags
  them; cards with empty feedback are untouched.

## Open questions

- Scope by `deck` or by `models`? (Managed models can span decks; a deck filter is convenient for
  the current single-deck flow.)
- Does the tool also **return** the JSON only, or also **persist** it next to `.compiled.md`?
  (Persisting helps the standalone refine command; returning-only keeps it stateless. Could do
  both: return always, persist if a path is passed.)
- Field-value snippets vs full field values in the payload (size vs completeness).
