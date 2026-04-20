---
name: compile-deck-context
description: Compile a deck's full context chain into a flat compiled file
disable-model-invocation: true
---

Compile a deck's full inheritance chain into a single flat file for use as an isolated system prompt.

Usage: `/compile-deck-context <deck>`

e.g. `/compile-deck-context spanish`

`<deck>` is a deck name (e.g., `spanish`, `english`, `instruments`).

## Step 1 — Resolve Deck Path

Search `decks/**/` for a directory whose name matches `<deck>`. The target is that directory (e.g., `decks/languages/spanish`).

If no match: report "Deck '<deck>' not found." and stop.

## Step 1b — Freshness Check

Run:
```
python3 .claude/scripts/compiled-is-fresh.py <resolved-deck-dir>
```

- Exit code 0 → already up-to-date. Report and stop:
  ```
  ✓ <deck> already up-to-date — compiled.md is newer than all inputs.
  ```
- Exit code 1 → proceed to Step 2.

## Step 2 — Depolymorphize

Run `/depolymorphize <resolved-deck-dir>`.

This produces `<resolved-deck-dir>/depolymorphized.md` with layer annotations.

## Step 3 — Merge to Human-Readable

Run `/compile <resolved-deck-dir>/depolymorphized.md`.

This produces `<resolved-deck-dir>/compiled.md` — a clean, flat document with no layer markers. This is the compiled output.

## Step 4 — Report

```
✓ Compiled <deck> → <resolved-deck-dir>/compiled.md
```
