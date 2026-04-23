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

Your primary job is **reordering and grouping**, not pruning. The depolymorphized file is ordered general → specific; the compiled file should read as one coherent spec where related content from every layer sits together.

### Merge rules

1. **Default = preserve.** Every rule, bullet, code-block entry, and prose line from every layer is carried into the output. Losing non-conflicting content is a bug.
2. **Group by semantic category.** When the same heading (e.g., `Input Rules`, `User Input Syntax`, `Tagging`, `Output Format`, `Quality Check`, `Card Design Rules`) appears in multiple layers, merge them into a single section of that name. Concatenate the content from general → specific inside the merged section.
3. **Override only on mutually exclusive conflicts.** A conflict is mutually exclusive when the two statements cannot both hold at once. When detected, the later (more specific) layer wins and the earlier statement is dropped. Examples:
   - Scalar config sharing a key: two different `deckName:` or `basicModel:` values.
   - Direct contradiction in prose: `Always generate X` vs `Do NOT generate X` targeting the same object.
   - A rule the specific layer explicitly supersedes (e.g., *"ignore the shared Tagging cap of 3–6; this deck uses 4–8"*).
   Non-exclusive elaborations — a new tag family, a new card type, an additional quality check — are **additive**. Keep both.
4. **Deduplicate only verbatim or near-verbatim repeats.** If the same bullet appears in two layers with identical meaning, keep one copy at its earliest applicable layer.
5. **Strip scaffolding.** Remove `# inheritable-*.md` headers and `---` separators entirely.
6. **Single unified document.** Output one H1 (the deck's name, e.g. `# Spanish Deck`) — not one H1 per layer. H2s are merged semantic sections (`Deck Config`, `Card Generation Rules`, `Tagging`, `Output Format`, `Quality Check`, …), each containing the merged content from every layer that contributed.

### Worked examples

**Additive merge** (non-conflicting bullets under the same heading):

Input:
```
### Quality Check          (from language layer)
- Is cloze actually improving retention?

### Quality Check          (from Spanish layer)
- Would a real Argentine say this?
```

Correct output:
```
### Quality Check
- Is cloze actually improving retention?
- Would a real Argentine say this?
```

Wrong output (drops the language-layer bullet):
```
### Quality Check
- Would a real Argentine say this?
```

**Mutually exclusive override** (same key, different concrete value):

Input:
```
cardtype::<type>     (from shared layer — placeholder)
cardtype::production / pattern / cloze     (from Spanish layer — concrete enumeration)
```

Correct output keeps only the Spanish line: the two cannot both be the enumeration of allowed `cardtype` values.

The final file should read as a single, self-contained specification that someone unfamiliar with the layering system can understand without any context about how it was assembled.

## Step 3 — Write Output

Read the existing `compiled.md` if it exists — this satisfies the Write tool's read-first constraint. Ignore its contents entirely; do not compare, diff, or merge.

Write to `<dir>/compiled.md` — in the same directory as the input file.

Example: `decks/languages/spanish/depolymorphized.md` → `decks/languages/spanish/compiled.md`

## Step 4 — Report

```
✓ Human-readable merge → <output-path>
```
