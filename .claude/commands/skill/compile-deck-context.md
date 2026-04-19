Compile a deck's full context-inheritance chain into a single flat file for use as an isolated system prompt.

Usage: `/skill:compile-deck-context <deck>`

e.g. `/skill:compile-deck-context spanish`

`<deck>` is a deck name (e.g., `spanish`, `english`, `instruments`).

## Step 1 — Resolve Deck Path

Search `decks/**/` for a directory whose name matches `<deck>`. The target is `decks/<...>/<deck>/context.md`.

If no match: report "Deck '<deck>' not found." and stop.

## Step 2 — Depolymorphize

Run `/skill:depolymorphize <resolved-context-path>`.

This produces `<resolved-context-path>.depolymorphized.md` with layer annotations.

## Step 3 — Merge to Human-Readable

Run `/skill:depolymorphize-human <resolved-context-path>`.

This produces `<resolved-context-path>.depolymorphized-human.md` — a clean, flat document with no layer markers. This is the compiled output.

## Step 4 — Report

```
✓ Compiled <deck> → <resolved-context-path>.depolymorphized-human.md
```
