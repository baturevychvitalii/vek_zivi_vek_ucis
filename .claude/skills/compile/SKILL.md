---
name: compile
description: Merge a depolymorphized file into one human-readable document
disable-model-invocation: true
---

Merge a depolymorphized file into a single coherent, human-readable document — no layers, no inheritance markers.

Usage: `/compile <path-to-depolymorphized.md>`

e.g. `/compile decks/languages/spanish/depolymorphized.md`

**Prerequisite:** The `depolymorphized.md` file must already exist at the given path. If it does not, tell the user to run `/depolymorphize <directory>` first.

## Step 1 — Read the Raw Depolymorphized File

Read the file at `<path-to-depolymorphized.md>`.

## Step 2 — Merge into a Single Document

Collapse the concatenated layers into one flat document:

- **Unique sections** (appear under only one file's content): include as-is.
- **Overlapping sections** (same heading appears in multiple files): last occurrence wins — files are ordered general → specific, so the final copy is the most specific. Inherited content that is not overridden is preserved and woven in naturally.
- **File name headers** (`# inheritable-*.md`) and `---` separators: remove entirely.

The output should read as a single, self-contained specification that someone unfamiliar with the layering system can understand without any context about how it was assembled.

## Step 3 — Write Output

Write to `<dir>/compiled.md` — in the same directory as the input file.

Example: `decks/languages/spanish/depolymorphized.md` → `decks/languages/spanish/compiled.md`

## Step 4 — Report

```
✓ Human-readable merge → <output-path>
```
