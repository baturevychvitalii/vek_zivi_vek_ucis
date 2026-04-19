---
name: depolymorphize
description: Flatten a context.md inheritance chain into a single annotated file
disable-model-invocation: true
---

Materialize the full context-inheritance chain for a `context.md` file into a single flat file — raw concatenation with layer annotations.

Usage: `/depolymorphize <path-to-context.md>`

e.g. `/depolymorphize decks/languages/spanish/context.md`

`<path>` is a project-root-relative path to any `context.md` file.

## Step 1 — Resolve the Ancestor Chain

Starting from the directory containing the target `context.md`, walk up toward the project root. Collect every `context.md` found in ancestor directories. Order: root-first, then downward to the target.

Example for `decks/languages/spanish/context.md`:
1. `decks/context.md`
2. `decks/languages/context.md`
3. `decks/languages/spanish/context.md`

Note: only look within the subtree that contains the target — stop at the project root. A `context.md` at the project root itself is not part of any deck hierarchy and should not be included unless the target is directly inside the root.

## Step 2 — Read All Layers

Read each `context.md` in the resolved order.

For each layer, scan for explicit read instructions matching the pattern:
```
read `filename.md`
```
(with or without surrounding text like "in this directory" or "first")

If found, read the referenced file, resolved relative to that `context.md`'s directory.

## Step 3 — Concatenate with Layer Annotations

Determine the total layer count N. For each layer, assign a label:
- Layer 1 of N: `General defaults`
- Layers 2 through N-1: `Domain-specific extension (narrows and may override above)`
- Layer N: `Specific rules (narrows and may override above)`
- If N == 1: just use `Full context` with no override language
- If N == 2: Layer 1 is `General defaults`, Layer 2 is `Specific rules (narrows and may override Layer 1)`

Format:

```
# Layer 1 of N — General defaults

(content)

---

# Layer 2 of N — Domain-specific extension (narrows and may override above)

(content)

---

# Layer N of N — Specific rules (narrows and may override above)

(content)
```

When a layer has referenced files (from "read X" instructions):
- Strip the "read X" instruction line from the layer content
- Append the referenced file's content within the same layer under:

```
### Referenced: <filename>

(content of referenced file)
```

## Step 4 — Write Output

Write the concatenated result to `<input-path>.depolymorphized.md` — next to the input file.

Example: `decks/languages/spanish/context.md` → `decks/languages/spanish/context.md.depolymorphized.md`

## Step 5 — Report

```
✓ Depolymorphized <path> → <output-path>
  Layers: N
  Inlined references: <list of filenames, or "none">
```
