---
name: depolymorphize
description: Flatten an inheritable-* file inheritance chain into a single annotated file
disable-model-invocation: true
---

<INHERITABLE_PREFIX> = inheritable-

Materialize the full inheritance chain for a directory into a single flat file — raw concatenation with layer annotations.

Usage: `/depolymorphize <path-to-directory>`

e.g. `/depolymorphize decks/languages/spanish`

`<path>` is a project-root-relative path to a directory.

## Step 1 — Resolve the Ancestor Chain

Starting from the target directory, walk up toward the project root. At each directory level, collect all files whose name starts with `<INHERITABLE_PREFIX>`, sorted alphabetically. Skip levels with no matching files. Order: root-first, then downward to the target.

Example for `decks/languages/spanish`:
1. `decks/` → `inheritable-deck-defaults.md`
2. `decks/languages/` → `inheritable-language-defaults.md`
3. `decks/languages/spanish/` → `inheritable-spanish.md`

Note: only look within the subtree that contains the target — stop at the project root. A matching file at the project root is not part of any deck hierarchy and should not be included unless the target is directly inside the root.

## Step 2 — Read All Layers

Read each collected file in the resolved order.

For each file, scan for explicit read instructions matching the pattern:
```
read `filename.md`
```
(with or without surrounding text like "in this directory" or "first")

If found, read the referenced file, resolved relative to that file's directory.

## Step 3 — Concatenate with Layer Annotations

Determine the total layer count N (one layer per directory depth, not per file). For each layer, assign a label:
- Layer 1 of N: `General defaults`
- Layers 2 through N-1: `Domain-specific extension (narrows and may override above)`
- Layer N: `Specific rules (narrows and may override above)`
- If N == 1: just use `Full context` with no override language
- If N == 2: Layer 1 is `General defaults`, Layer 2 is `Specific rules (narrows and may override Layer 1)`

Multiple files at the same directory depth are concatenated alphabetically within that layer before the layer header is applied.

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

When a file has referenced files (from "read X" instructions):
- Strip the "read X" instruction line from the file's content
- Append the referenced file's content within the same layer under:

```
### Referenced: <filename>

(content of referenced file)
```

## Step 4 — Write Output

Write the concatenated result to `<target-dir>/depolymorphized.md`.

Example: `decks/languages/spanish` → `decks/languages/spanish/depolymorphized.md`

## Step 5 — Report

```
✓ Depolymorphized <path> → <output-path>
  Layers: N
  Inlined references: <list of filenames, or "none">
```
