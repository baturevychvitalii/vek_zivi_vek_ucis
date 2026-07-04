---
name: compile
description: Merge a preprocessed file into one human-readable document
disable-model-invocation: false
context: fork
---

Merge a preprocessed file into a single coherent, human-readable document — no layers.

Usage: `/context-compiler:compile <path-to-file.preprocessed.md>`

e.g. `/context-compiler:compile path/to/file.preprocessed.md`

**Prerequisite:** The `.preprocessed.md` file must already exist. If it does not, tell the user to run `/context-compiler:compile-context <file.md>` first.

## Step 1 — Read the Raw Preprocessed File

Read the file at `<path-to-file.preprocessed.md>`.

## Step 2 — Merge into a Single Document

Your primary job is **reordering and grouping**, not pruning. The preprocessed file is ordered general → specific; the compiled file should read as one coherent spec where related content from every layer sits together.

### Merge rules

1. **Default = preserve.** Every rule, bullet, code-block entry, and prose line from every layer is carried into the output. Losing non-conflicting content is a bug.
2. **Group by semantic category.** When the same heading (e.g., `Input Rules`, `User Input Syntax`, `Tagging`, `Output Format`, `Quality Check`, `Card Design Rules`) appears in multiple layers, merge them into a single section of that name. Concatenate the content from general → specific inside the merged section.
3. **Override only on mutually exclusive conflicts.** A conflict is mutually exclusive when the two statements cannot both hold at once. When detected, the later (more specific) layer wins and the earlier statement is dropped. Examples:
   - Scalar config sharing a key: two different values for the same key (e.g. `theme:` or `outputFormat:`).
   - Direct contradiction in prose: `Always generate X` vs `Do NOT generate X` targeting the same object.
   - A rule the specific layer explicitly supersedes (e.g., *"ignore the shared tag limit of 3–6; this context uses 4–8"*).
   Non-exclusive elaborations — a new tag family, a new card type, an additional quality check — are **additive**. Keep both.
4. **Deduplicate only verbatim or near-verbatim repeats.** If the same bullet appears in two layers with identical meaning, keep one copy at its earliest applicable layer.
5. **Strip scaffolding.** Remove `# *.md` headers and `---` separators entirely.
6. **Single unified document.** Output one H1 (the subject's name, e.g. `# Spanish`) — not one H1 per layer. H2s are merged semantic sections (`Processing Rules`, `Output Format`, `Quality Check`, …), each containing the merged content from every layer that contributed.

### Worked examples

**Additive merge** (non-conflicting bullets under the same heading):

Input:
```
### Quality Check          (from shared layer)
- Is the content accurate?

### Quality Check          (from specific layer)
- Does the phrasing match the target audience?
```

Correct output:
```
### Quality Check
- Is the content accurate?
- Does the phrasing match the target audience?
```

Wrong output (drops the shared-layer bullet):
```
### Quality Check
- Does the phrasing match the target audience?
```

**Mutually exclusive override** (same key, different concrete value):

Input:
```
outputType::<type>     (from shared layer — placeholder)
outputType::summary / analysis / report     (from specific layer — concrete enumeration)
```

Correct output keeps only the specific-layer line: the two cannot both be the enumeration of allowed `outputType` values.

The final file should read as a single, self-contained specification that someone unfamiliar with the layering system can understand without any context about how it was assembled.

## Step 3 — Write Output

The output path is derived from the input: replace `.preprocessed.md` with `.compiled.md`.

e.g. `spanish.preprocessed.md` → `spanish.compiled.md`

Read the existing output file if it exists — this satisfies the Write tool's read-first constraint. Ignore its contents entirely; do not compare, diff, or merge.

Write to the derived output path.

## Step 4 — Report

```
✓ Human-readable merge → <output-path>
```
