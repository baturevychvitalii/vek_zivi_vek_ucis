---
name: compile
description: Merge a depolymorphized file into one human-readable document
disable-model-invocation: true
---

Merge a depolymorphized context file into a single coherent, human-readable document — no layers, no inheritance markers.

Usage: `/compile <path-to-context.md>`

e.g. `/compile decks/languages/spanish/context.md`

**Prerequisite:** The `.depolymorphized.md` file must already exist at `<path>.depolymorphized.md`. If it does not, tell the user to run `/depolymorphize <path>` first.

## Step 1 — Read the Raw Depolymorphized File

Read `<path>.depolymorphized.md`.

## Step 2 — Merge into a Single Document

Collapse the layered structure into one flat document:

- **Unique sections** (exist in only one layer): include as-is.
- **Overlapping sections** (same heading appears in multiple layers): merge them. The most specific (deepest layer) version wins for conflicting fields. Inherited content that is not overridden is preserved and woven in naturally.
- **Layer headers** (`# Layer N of M — ...`) and `---` separators: remove entirely.
- **"Referenced" sub-headers** (`### Referenced: filename`): remove the sub-header, keep the content integrated into the appropriate section.
- **Override language** ("extends", "narrows", "may override"): remove — the result is the final resolved state, not a description of the process.

The output should read as a single, self-contained specification that someone unfamiliar with the layering system can understand without any context about how it was assembled.

## Step 3 — Write Output

Write to `<path>.compiled.md` — next to the input file.

Example: `decks/languages/spanish/context.md` → `decks/languages/spanish/context.md.compiled.md`

## Step 4 — Report

```
✓ Human-readable merge → <output-path>
```
